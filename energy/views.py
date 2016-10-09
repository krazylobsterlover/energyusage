from flask import render_template, url_for, jsonify, redirect, flash, request
from app import app
from models import get_energy_chart_data, get_data_range
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
import arrow

@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/usage/')
@app.route('/usage/<int:report_year>/')
@app.route('/usage/<int:report_year>/<int:report_month>')
def usage(report_year=None, report_month=None):

    meter_id = 3044076134
    # Specify default month to report on
    if report_year is None or report_month is None:
        a = arrow.utcnow()
        report_year = a.year
        report_month = a.month
        return redirect(url_for('usage', report_year=report_year, report_month=report_month))

    month_start = arrow.get(report_year, report_month, 1)

    # Get the date range data exists for
    first_record, last_record = get_data_range(meter_id)
    first_record = arrow.get(first_record).replace(months=-1)
    last_record = arrow.get(last_record)

    next_month = month_start.replace(months=+1)
    if next_month >= last_record:
        next_month_data = False
    else:
        next_month_data = True

    prev_month = month_start.replace(months=-1)
    if prev_month <= first_record:
        prev_month_data = False
    else:
        prev_month_data = True

    month_navigation = {'prev_year': prev_month.year,
                        'prev_month': prev_month.month,
                        'prev_enabled': prev_month_data,
                        'next_year': next_month.year,
                        'next_month': next_month.month,
                        'next_enabled': next_month_data
                        }

    return render_template('usage.html', meter_id = meter_id,
                           report_year = report_year, report_month = report_month,
                           month_navigation = month_navigation,
                           month_desc = month_start.format('MMM YY'),
                           start_date = month_start.format('YYYY-MM-DD'),
                           end_date = next_month.format('YYYY-MM-DD')
                           )


@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/energy_data/')
@app.route('/energy_data/<meter_id>.json', methods=['POST', 'GET'])
def energy_data(meter_id=None):
    if meter_id is None:
        return 'json chart api'
    else:
        params = request.args.to_dict()
        if params['start_date']:
            start_date = params['start_date']
        if params['end_date']:
            end_date = params['end_date']
        flotData = get_energy_chart_data(meter_id, start_date, end_date)
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