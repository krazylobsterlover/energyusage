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
    interval = db.Column(db.Integer)
    imp = db.Column(db.Integer)
    exp = db.Column(db.Integer)


def get_data_range(meter_id):
    """ Get the minimum and maximum date ranges with data
    """
    min_date = db.session.query(func.min(Energy.reading_date)).filter(Energy.user_id==meter_id).scalar()
    max_date = db.session.query(func.max(Energy.reading_date)).filter(Energy.user_id==meter_id).scalar()
    return (min_date, max_date)


class User(db.Model):
    """ A user account
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True)
    _password = db.Column(db.String(128))
    efergy_token = db.Column(db.String(32))


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

    def _set_efergy_token(self, token):
        self.efergy_token = token

    def get_efergy_token(self):
        self.efergy_token

