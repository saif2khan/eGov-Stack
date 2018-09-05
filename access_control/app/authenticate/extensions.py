# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory located in app.py."""
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from authenticate.settings import Config
from flask_httpauth import HTTPBasicAuth
from flask_mail import Mail

bcrypt = Bcrypt()
login_manager = LoginManager()
db = SQLAlchemy()
migrate = Migrate()
auth = HTTPBasicAuth()
api = Api(prefix='/api/v1')
mail = Mail()
