from flask import render_template, jsonify
from app import app
from models import get_energy_chart_data


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