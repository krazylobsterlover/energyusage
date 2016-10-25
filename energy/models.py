from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column, DateTime, Float, between, func
from sqlalchemy.sql import select
import arrow
from sqlalchemy.ext.hybrid import hybrid_property
from . import bcrypt, db


metadata = MetaData()
meter_readings = Table('interval_readings', metadata,
    Column('reading_date', DateTime, primary_key=True),
    Column('ch1', Float, nullable=False),
)


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
    file_name = 'data/' + str(meter_id) + '.db'
    engine = create_engine('sqlite:///'+file_name, echo=True)
    conn = engine.connect()
    s = select([func.min(meter_readings.c.reading_date),
               func.max(meter_readings.c.reading_date)
               ])
    data = conn.execute(s).fetchall()
    return data[0]


def get_energy_data(meter_id, start_date, end_date):
    """ Get energy data for a meter
    """
    file_name = 'data/' + str(meter_id) + '.db'
    engine = create_engine('sqlite:///'+file_name, echo=True)
    conn = engine.connect()
    s = select([meter_readings]).where(
        between(meter_readings.c.reading_date, start_date, end_date))
    data = conn.execute(s).fetchall()
    return data


def get_energy_chart_data(meter_id, start_date, end_date):
    """ Return json object for flot chart
    """
    data = get_energy_data(meter_id, start_date, end_date)

    chartdata = {}
    chartdata['label'] = 'Energy Profile'
    chartdata['consumption'] = []

    for row in data:
        dTime = arrow.get(row[0])
        ts = int(dTime.timestamp * 1000)
        chartdata['consumption'].append([ts, row[1]])

    return chartdata
