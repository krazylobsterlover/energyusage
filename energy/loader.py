import csv
import arrow
from .models import User, Energy
from . import db
from flask import flash


def import_meter_data(user_name, file_path):
    """ Load data from the user uploaded csv file into the database
    """
    user = User.query.filter_by(username=user_name).first()
    new_records = 0
    skipped_records = 0
    for row in load_from_file(file_path):
        reading_date = parse_date(row[0])
        imp = int(row[1])
        exp = int(row[2])
        if Energy.query.filter_by(user_id=user.id, reading_date=reading_date).first():
            # Record already exists
            skipped_records += 1
        else:
            energy = Energy(user_id=user.id, reading_date=reading_date, imp=imp, exp=exp)
            db.session.add(energy)
            new_records += 1
    db.session.commit()
    return new_records, skipped_records


def parse_date(date_string):
    try:
        return arrow.get(date_string).datetime
    except arrow.parser.ParserError:
        return arrow.get(date_string, 'DD/MM/YYYY HH:mm:ss').datetime
    except:
        raise


def load_from_file(file_path):
    """ Return load data from csv
    """
    with open(file_path, newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        h = next(reader, None)  # first row is headings
        if h[0:3] == ['READING_DATETIME', 'IMP', 'EXP']:
            for row in reader:
                yield row
        else:
            flash('File was not in the correct format.')