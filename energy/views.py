from flask import render_template, url_for, jsonify, redirect, flash
from app import app
from models import get_energy_chart_data
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired


@app.route('/')
def homepage():
    return render_template('index.html')


@app.route('/usage/')
def usage():
    return render_template('usage.html')


@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/energy_data/')
@app.route('/energy_data/<meterId>.json')
def energy_data(meterId=3044076134):
    if meterId is None:
        return 'json chart api'
    else:
        flotData = get_energy_chart_data(meterId)
        return jsonify(flotData)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(u'Sorry. User login is not yet supported ...')
        return redirect(url_for('login'))
    return render_template('login.html', form=form)


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])