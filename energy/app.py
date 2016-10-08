from flask import Flask, render_template, jsonify
from getchartdata import get_energy_chart_data
app = Flask(__name__, static_path='/static', static_folder='static/')


@app.route('/')
def index():
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


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=23948, threaded=True, debug=True)

