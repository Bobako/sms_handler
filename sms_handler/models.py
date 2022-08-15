from flask_login import UserMixin

from sms_handler import db, manager


class User(db.Model, UserMixin):
    __tablename__ = "user"
    login = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)
    is_authenticated = db.Column(db.Boolean)
    is_active = True
    is_anonymous = False

    def __init__(self, login, password):
        self.login = login
        self.password = password

    def get_id(self):
        return self.login


class Message(db.Model):
    __tablename__ = "sms"
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime)
    phone = db.Column(db.String)
    text = db.Column(db.String)
    primary_service_status = db.Column(db.Boolean)
    primary_service_status_text = db.Column(db.String)
    secondary_service_status = db.Column(db.Boolean)
    secondary_service_id = db.Column(db.String)
    secondary_service_status_text = db.Column(db.String)

    def __init__(self, id_, datetime, phone, text, primary_service_status, secondary_service_status,
                 primary_service_status_text="", secondary_service_status_text=""):
        self.id = id_
        self.datetime = datetime
        self.phone = phone
        self.text = text
        self.primary_service_status = primary_service_status
        self.secondary_service_status = secondary_service_status
        self.primary_service_status_text = primary_service_status_text
        self.secondary_service_status_text = secondary_service_status_text
        self.secondary_service_id = None

    def __repr__(self):
        return f"{self.id}, {self.phone}, {self.text}, {self.primary_service_status}"


class Sub(db.Model):
    __tablename__ = "sub"
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String)
    name = db.Column(db.String)
    last_message_datetime = db.Column(db.DateTime)

    def __init__(self, phone, name="", last_message_datetime=None):
        self.phone = phone
        self.name = name
        self.last_message_datetime = last_message_datetime


@manager.user_loader
def load_user(user_phone):
    return User.query.get(user_phone)
