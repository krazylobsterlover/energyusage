from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__, static_path='/static', static_folder='static/')
app.config.from_object('config.Configuration')
toolbar = DebugToolbarExtension(app)
db = SQLAlchemy(app)