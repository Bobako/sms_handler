from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from sms_handler.cfg import config

app = Flask(__name__)
app.secret_key = config["SITE"]["secret_key"]
app.config['SQLALCHEMY_DATABASE_URI'] = config["DATABASE"]["uri"]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
manager = LoginManager(app)

from sms_handler import models, routes
from sms_handler.sms_api import SMSAPI
from sms_handler.database import create_admin

db.create_all()
create_admin(db.session, models.User)
sms_api_worker = SMSAPI.from_config(db.session)
