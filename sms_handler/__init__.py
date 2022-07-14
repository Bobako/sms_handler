from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = 'some secret salt'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
manager = LoginManager(app)

from sms_handler import models, routes
from sms_handler.database import create_admin
from sms_handler.sms_service import SMSService

db.create_all()
create_admin(db.session, models.User)
service = SMSService.from_config(db.session)
