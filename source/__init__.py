from flask import Flask
from config import Config
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from .backend import check_answer, log

source = Flask(__name__)
source.config.from_object(Config)

db = SQLAlchemy(source)
lm = LoginManager()
lm.init_app(source)
lm.login_view = 'login'

from source import route, form, model
