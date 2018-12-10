from config import Config
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from .backend import *

source = Flask(__name__)
source.config.from_object(Config)

db = SQLAlchemy(source)
lm = LoginManager()
lm.init_app(source)
lm.login_view = 'login'

from source import route, form, model
