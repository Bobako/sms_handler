from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from sms_handler.cfg import config
from sms_handler.sms_api import SMSAPI
from sms_handler.database import create_admin

app = Flask(__name__)
app.secret_key = 'some secret salt'
app.config['SQLALCHEMY_DATABASE_URI'] = config["DATABASE"]["uri"]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
manager = LoginManager(app)

from sms_handler import models

db.create_all()
create_admin(db.session, models.User)
sms_api = SMSAPI.from_config(db.session)

from sms_handler import routes
