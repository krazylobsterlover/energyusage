from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.config.from_object('config')
toolbar = DebugToolbarExtension(app)
db = SQLAlchemy(app)