import csv
import io
import os
import arrow
from .models import User, Energy
from . import db
from flask import flash
import logging


def export_meter_data(user_id):

    header = ['READING_DATE', 'IMP', 'EXP']
    data = get_meter_data(user_id)
    return construct_csv(header, data)


def get_meter_data(user_id):
    readings = Energy.query.filter(Energy.user_id==user_id)
    for r in readings:
        yield [r.reading_date, r.imp, r.exp]


def construct_csv(header, data):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(header)
    for row in data:
        writer.writerow(row)
    return output.getvalue()


def import_meter_data(user_name, file_path):
    """ Load data from the user uploaded csv file into the database
    """
    user = User.query.filter_by(username=user_name).first()
    new_records = 0
    skipped_records = 0
    failed_records = 0
    for row in load_from_file(file_path):
        try:
            reading_date = parse_date(row[0])
        except:
            msg = '{} is not a date format'.format(row[0])
            logging.error(msg)
            failed_records += 1
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
    return new_records, skipped_records, failed_records


def parse_date(date_string):
    try:
        return arrow.get(date_string).datetime
    except arrow.parser.ParserError:
        try:
            return arrow.get(date_string, 'DD/MM/YYYY HH:mm:ss').datetime
        except arrow.parser.ParserError:
            try:
                return arrow.get(date_string, 'DD/MM/YYYY H:mm').datetime
            except arrow.parser.ParserError:
                return arrow.get(date_string, 'D/MM/YYYY H:mm').datetime
    except:
        raise


def load_from_file(file_path):
    """ Return load data from csv
    """
    ext = os.path.splitext(file_path)[1]
    if ext == 'csv':
        flash('File should be .csv not ' + str(ext), category='danger')

    with open(file_path, newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        h = next(reader, None)  # first row is headings
        if h[0:3] == ['READING_DATETIME', 'IMP', 'EXP']:
            for row in reader:
                yield row
        else:
            flash('CSV was not in the correct format.', category='danger')