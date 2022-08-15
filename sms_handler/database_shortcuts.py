import datetime
import random

from sms_handler.cfg import config
from sms_handler.models import Sub, Message


def create_admin(session, user_class):
    """Creates default user if not already exists"""
    if not session.query(user_class).first():
        session.add(user_class(
            config["DATABASE"]["default_admin_login"],
            config["DATABASE"]["default_admin_password"],
        ))
        session.commit()


def create_dummy_data(session, ):
    if not session.query(Sub).first():
        for sub in [
            Sub(89990123456, "Игорь", datetime.datetime.now() - datetime.timedelta(days=random.randint(2, 30))),
            Sub(89990839057, "", datetime.datetime.now() - datetime.timedelta(days=random.randint(2, 30))),
            Sub(89991325655, "Виктор", datetime.datetime.now() - datetime.timedelta(days=random.randint(2, 30))),
            Sub(89991235123, "", datetime.datetime.now() - datetime.timedelta(days=random.randint(2, 30))),
            Sub(89991235132, "Игорь", datetime.datetime.now() - datetime.timedelta(days=random.randint(2, 30))),
            Sub(89992351235, "Валера", datetime.datetime.now() - datetime.timedelta(days=random.randint(2, 30))),
            Sub(89992343244, "", datetime.datetime.now() - datetime.timedelta(days=random.randint(2, 30))),
            Sub(89992342341, "Игорь", datetime.datetime.now() - datetime.timedelta(days=random.randint(2, 30))),
            Sub(89991341344, "Виктор", datetime.datetime.now() - datetime.timedelta(days=random.randint(2, 30))),
            Sub(89993333122, "Валера", datetime.datetime.now() - datetime.timedelta(days=random.randint(2, 30))),
            Sub(89993435332, "", datetime.datetime.now() - datetime.timedelta(days=random.randint(2, 30))),
            Sub(89996766789, "Виктор", datetime.datetime.now() - datetime.timedelta(days=random.randint(2, 30))),
            Sub(89994575676, "", datetime.datetime.now() - datetime.timedelta(days=random.randint(2, 30))),
        ]:
            session.add(sub)
    if not session.query(Message).first():
        for i in range(30):
            primary_status = bool(random.randint(0, 1))
            secondary_status = bool(random.randint(0, 1))
            session.add(
                Message(1, datetime.datetime.now() - datetime.timedelta(days=random.randint(2, 30)),
                        random.randint(89990000000, 89999999999), f"Ваш код: {random.randint(1000, 9999)}",
                        primary_status, secondary_status,
                        ["Ошибка", "Успех"][primary_status], ["Ошибка", "Успех"][secondary_status]
                        ))
    session.commit()
