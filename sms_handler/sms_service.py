import json
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


class SMSService:
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

    @staticmethod
    def from_config(session):
        """Factory; all params from config"""
        return SMSService(
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
        r = requests.get(url)
        if r.status_code != 200:
            logging.error(f"{r.status_code} response status code while 'sms_service.get_sms'")
            return []
        if "error" in r.json():
            logging.error(f"{r.json()['error']} response  while 'sms_service.get_sms'")
            return []
        sms_list = []
        for sms_dict in r.json():
            if sms_dict["status"] == 25:  # так как по тз обрабатываем только смс с статусом недоступный номер
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
        """Create sms and subscribers objects in database"""
        for sms in sms_list:
            if sms.datetime > datetime.datetime.now() - datetime.timedelta(seconds=60*4+10):
                if not self.session.query(Message).filter(Message.id == sms.id).first():
                    is_sent, status_str = self.send_sms(sms.text, sms.phone)
                    sms.secondary_service_status = is_sent
                    sms.secondary_service_status_text = status_str
                    self.session.add(sms)
                    if sub := self.session.query(Sub).filter(Sub.phone == sms.phone).first():
                        if is_sent:
                            sub.last_sms_datetime = sms.datetime
                    else:
                        sub = Sub(sms.phone, last_sms_datetime=sms.datetime if is_sent else None)
                        self.session.add(sub)
                    self.session.commit()

    def run(self):
        while True:
            sms_list = self.get_sms()
            self.add_sms(sms_list)
            time.sleep(121)

    def send_sms(self, text: str, phone: str) -> (bool, str):
        """Send SMS via https://sms-fly.ua/. Returns is_sent and status"""
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
        r = requests.post("https://sms-fly.ua/api/v2/api.php", json=data_dict_)
        code = r.status_code
        if code != 200:
            return False, CODES.get(code, "Error")

        try:
            message_status = r.json()["data"]["sms"]["status"].lower().capitalize()
        except Exception:
            return False, "Error"
        else:
            return True, message_status


if __name__ == '__main__':
    pass
