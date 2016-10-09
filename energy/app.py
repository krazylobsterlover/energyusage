from flask import Flask

app = Flask(__name__, static_path='/static', static_folder='static/')
app.config.from_object('config.Configuration')