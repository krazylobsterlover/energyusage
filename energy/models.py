from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column, DateTime, Float, Integer, between, func
from sqlalchemy.sql import select
import arrow
from sqlalchemy.ext.hybrid import hybrid_property
from . import bcrypt, db, app


class Energy(db.Model):
    """ The energy data for a user
    """
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    reading_date = db.Column(db.DateTime, primary_key=True)
    imp = db.Column(db.Integer)
    exp = db.Column(db.Integer)


class User(db.Model):
    """ A user account
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True)
    _password = db.Column(db.String(128))


    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def _set_password(self, plaintext):
        self._password = bcrypt.generate_password_hash(plaintext)

    def is_correct_password(self, plaintext):
        return bcrypt.check_password_hash(self._password, plaintext)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.id

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False


def get_data_range(meter_id):
    """ Get the minimum and maximum date ranges with data
    """
    min_date = db.session.query(func.min(Energy.reading_date)).filter(Energy.user_id==1).scalar()
    max_date = db.session.query(func.max(Energy.reading_date)).filter(Energy.user_id==1).scalar()
    return (min_date, max_date)


def get_energy_data(meter_id, start_date, end_date):
    """ Get energy data for a meter
    """
    readings = Energy.query.filter(Energy.user_id==1)
    readings = readings.filter(Energy.reading_date>=start_date)
    readings = readings.filter(Energy.reading_date<=end_date).all()
    return readings


def get_energy_chart_data(meter_id, start_date, end_date):
    """ Return json object for flot chart
    """
    chartdata = {}
    chartdata['label'] = 'Energy Profile'
    chartdata['consumption'] = []

    for r in get_energy_data(meter_id, start_date, end_date):
        dTime = arrow.get(r.reading_date)
        ts = int(dTime.timestamp * 1000)
        imp = r.imp
        chartdata['consumption'].append([ts, imp])

    return chartdata
