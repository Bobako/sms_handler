import queue
import time
from threading import Lock

import requests
import datetime
import logging

from sms_handler.models import Message, Sub
from sms_handler.cfg import config

lock = Lock()

CODES = {
    400: "BadRequest",
    403: "Forbidden",
    422: "UnprocessableEntity",
    500: "InternalError",
    502: "BadGateway",
}


class SMSAPI:
    def __init__(self,
                 session,
                 login: str,
                 password: str,
                 fly_sms_auth_key: str,
                 fly_sms_service_name: str = "",
                 smsc_fmt: int = 3,  # 3 for json
                 ):
        self.session = session
        self.login = login
        self.password = password
        self.smsc_fmt = smsc_fmt
        self.fly_sms_auth_key = fly_sms_auth_key
        self.fly_sms_service_name = fly_sms_service_name
        self.auto_send = False
        self.pending_sms = queue.Queue()

    @staticmethod
    def from_config(session):
        """Factory; all params from config"""
        return SMSAPI(
            session=session,
            login=config["SMS_SERVICE"]["smsc_login"],
            password=config["SMS_SERVICE"]["smsc_password"],
            fly_sms_auth_key=config["SMS_SERVICE"]["sms_fly_auth_key"],
            fly_sms_service_name=config["SMS_SERVICE"]["sms_fly_service_name"]
        )

    def get_sms(self,
                start: datetime.datetime | None = None,
                end: datetime.datetime | None = None,
                cnt=1000  # max amount of sms
                ) -> list[Message]:
        """ Query sms info from smsc service"""
        if not start or not end:
            start = datetime.datetime.now() - datetime.timedelta(days=1)
            end = start + datetime.timedelta(days=1)
        url = f"https://smsc.ua/sys/get.php?get_messages=1&" \
              f"login={self.login}" \
              f"&psw={self.password}" \
              f"&start={start.strftime('%d.%m.%Y')}" \
              f"&end={end.strftime('%d.%m.%Y')}" \
              f"&fmt={self.smsc_fmt}" \
              f"&cnt={cnt}"
        try:
            r = requests.get(url)
        except Exception as ex:
            logging.error(f"{ex} while 'sms_service.get_sms'")
            return []
        if r.status_code != 200:
            logging.error(f"{r.status_code} response status code while 'sms_service.get_sms'")
            return []
        if "error" in r.json():
            logging.error(f"{r.json()['error']} response  while 'sms_service.get_sms'")
            return []
        sms_list = []
        for sms_dict in r.json():
            if sms_dict["status"] == 25:  # так как по тз обрабатываем только смс со статусом недоступный номер
                sms_list.append(Message(int(sms_dict['int_id']),
                                        datetime.datetime.strptime(sms_dict['send_date'], "%d.%m.%Y %H:%M:%S"),
                                        sms_dict['phone'],
                                        sms_dict['message'],
                                        False,  # Так как успешные смс не обрабатываем, всегда фолс
                                        False,
                                        sms_dict['status_name'],
                                        ""
                                        ))
        return sms_list

    def add_sms(self, sms_list: list[Message]):
        """Create sms and subscribers objects in database, calls send_sms method if needed.
        Checks if pending_sms (from previous add_sms calls) was sent"""

        for _ in range(self.pending_sms.qsize()):
            sms_id = self.pending_sms.get()
            sms_status_text = self.get_message_status(sms_id)
            message = self.session.query(Message).filter(Message.secondary_service_id == sms_id).one()
            message.secondary_service_status_text = sms_status_text
            is_sent = sms_status_text in ["SENT", "DELIVRD", "VIEWED"]
            message.secondary_service_status = is_sent
            if is_sent:
                sub = self.session.query(Sub).filter(Sub.phone == message.phone).first()
                sub.last_sms_datetime = message.datetime
            elif sms_status_text in ["ACCEPTD", "PENDING", "INPROGRESS", "MODERATION"]:
                self.pending_sms.put(sms_id)  # статус будет проверен снова в следующий раз
        self.session.commit()

        for sms in sms_list:
            if sms.datetime > datetime.datetime.now() - datetime.timedelta(seconds=60 * 4 + 10):
                if not self.session.query(Message).filter(Message.id == sms.id).first():
                    status_str, sms_id = "Не отправлялось", ""
                    if self.auto_send:
                        status_str, sms_id = self.send_sms(sms.text, sms.phone)
                    sms.secondary_service_id = sms_id
                    sms.secondary_service_status = False
                    sms.secondary_service_status_text = status_str

                    self.session.add(sms)
                    if not self.session.query(Sub).filter(Sub.phone == sms.phone).first():
                        sub = Sub(sms.phone)
                        self.session.add(sub)

                    if status_str == "ACCEPTD":
                        self.pending_sms.put(sms_id)
        self.session.commit()

    def run(self, auto_send=False):
        self.auto_send = auto_send
        while True:
            now = datetime.datetime.now()
            if now.minute % 2 == 0 and now.second in [0, 1, 2]:
                sms_list = self.get_sms()
                self.add_sms(sms_list)
                time.sleep(3)
            else:
                time.sleep(1)

    def send_sms(self, text: str, phone: str) -> (str, str):
        """Send SMS via https://sms-fly.ua/. Returns text_status and message_id in service """
        data_dict_ = {
            "auth": {
                "key": self.fly_sms_auth_key,
            },
            "action": "SENDMESSAGE",
            "data": {
                "recipient": phone,
                "channels": [
                    "sms"
                ],
                "sms": {
                    "source": self.fly_sms_service_name,
                    "ttl": 1440,
                    "text": text
                }
            }
        }
        try:
            r = requests.post("https://sms-fly.ua/api/v2/api.php", json=data_dict_)
        except Exception as ex:
            return "Request error", ""
        code = r.status_code
        if code != 200:
            return CODES.get(code, "Error"), ""

        try:
            message_status = r.json()["data"]["sms"]["status"].lower().capitalize()
            message_id = r.json()["data"]["messageID"]
        except Exception:
            return "Error", ""
        else:
            return message_status, message_id

    def get_message_status(self, message_id):
        """Check if sms was sent. Returns text_status"""
        data_dict_ = {
            "auth": {
                "key": self.fly_sms_auth_key,
            },
            "action": "GETMESSAGESTATUS",
            "data": {
                "messageID": message_id
            }}
        try:
            r = requests.post("https://sms-fly.ua/api/v2/api.php", json=data_dict_)
        except Exception as ex:
            return "Request error"

        code = r.status_code
        if code != 200:
            return CODES.get(code, "Error")

        try:
            message_status = r.json()["data"]["sms"]["status"].lower().capitalize()
        except Exception:
            return "Error"
        else:
            return message_status


if __name__ == '__main__':
    pass
