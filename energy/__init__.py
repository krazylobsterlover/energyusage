from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)
app.config.from_object('config')
toolbar = DebugToolbarExtension(app)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from .models import User

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "signin"


@login_manager.user_loader
def load_user(userid):
    return User.query.filter(User.id==userid).first()
