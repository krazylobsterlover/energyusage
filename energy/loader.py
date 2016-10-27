import csv
import arrow
from .models import User, Energy
from . import db



def import_meter_data(user_name, file_path):
    """ Load data from the user uploaded csv file into the database
    """
    user = User.query.filter_by(username=user_name).first()
    for row in load_from_file(file_path):
        reading_date = arrow.get(row[0]).datetime
        imp = int(row[1])
        exp = int(row[2])
        if Energy.query.filter_by(user_id=user.id, reading_date=reading_date).first():
            # Record already exists
            pass
        else:
            energy = Energy(user_id=user.id, reading_date=reading_date, imp=imp, exp=exp)
            db.session.add(energy)
    db.session.commit()


def load_from_file(file_path):
    """ Return load data from csv
    """
    with open(file_path, newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        h = next(reader, None)  # first row is headings
        if h == ['READING_DATETIME', 'IMP', 'EXP']:
            for row in reader:
                yield row
