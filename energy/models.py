from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column, DateTime, Float, between
from sqlalchemy.sql import select, text

import arrow

metadata = MetaData()
meter_readings = Table('interval_readings', metadata,
    Column('reading_date', DateTime, primary_key=True),
    Column('ch1', Float, nullable=False),
)

def get_energy_chart_data(meterId, start_date="2016-09-01",
                          end_date="2016-10-01"):
    """ Return json object for flot chart
    """
    engine = create_engine('sqlite:///../data/'+ str(meterId) + '.db', echo=True)
    conn = engine.connect()
    s = select([meter_readings]).where(between(meter_readings.c.reading_date, start_date, end_date))
    data = conn.execute(s).fetchall()

    chartdata = {}
    chartdata['label'] = 'Energy Profile'
    chartdata['consumption'] = []

    for row in data:
        dTime = arrow.get(row[0])
        ts = int(dTime.timestamp * 1000)
        chartdata['consumption'].append([ts, row[1]])

    return chartdata
