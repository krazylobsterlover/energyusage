from flask import render_template, url_for, jsonify, redirect, flash, request
from flask_login import login_user, logout_user, login_required, current_user
import os
import arrow
from werkzeug.utils import secure_filename
from . import app, db
from .models import User
from .models import get_energy_chart_data, get_data_range
from .loader import import_meter_data
from .forms import UsernamePasswordForm, FileForm


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=["GET", "POST"])
@login_required
def upload():
    form = FileForm()
    if form.validate_on_submit():
        filename = secure_filename(current_user.username+'.csv')
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        form.upload_file.data.save(file_path)
        import_meter_data(current_user.username, file_path)
        flash('Meter data saved to database')
        return redirect(url_for('index'))
    return render_template('upload.html', form=form)


@app.route('/signup', methods=["GET", "POST"])
def signup():
    form = UsernamePasswordForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User created!')
        return redirect(url_for('index'))
    return render_template('signup.html', form=form)


@app.route('/signin', methods=["GET", "POST"])
def signin():
    form = UsernamePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first_or_404()
        if user.is_correct_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        else:
            return redirect(url_for('signin'))
    return render_template('signin.html', form=form)


@app.route('/signout')
def signout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/usage/')
@app.route('/usage/<int:report_year>/')
@app.route('/usage/<int:report_year>/<int:report_month>')
@login_required
def usage(report_year=None, report_month=None):
    user_id = User.query.filter_by(username=current_user.username).first()
    # Specify default month to report on
    if report_year is None or report_month is None:
        a = arrow.utcnow()
        report_year = a.year
        report_month = a.month
        return redirect(url_for('usage', report_year=report_year, report_month=report_month))

    month_start = arrow.get(report_year, report_month, 1)

    # Get the date range data exists for
    first_record, last_record = get_data_range(user_id)
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

    return render_template('usage.html', meter_id = user_id,
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
@login_required
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
