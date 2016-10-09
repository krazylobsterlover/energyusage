from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_path='/static', static_folder='static/')
app.config.from_object('config.Configuration')
db = SQLAlchemy(app)