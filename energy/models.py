from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column, DateTime, Float, between, func
from sqlalchemy.sql import select
import arrow


metadata = MetaData()
meter_readings = Table('interval_readings', metadata,
    Column('reading_date', DateTime, primary_key=True),
    Column('ch1', Float, nullable=False),
)

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
