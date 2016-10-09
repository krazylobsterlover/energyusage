from sqlalchemy import create_engine
from sqlalchemy.sql import text
import arrow


def get_energy_chart_data(meterId, start_date="2016-09-01",
                          end_date="2016-10-01"):
    """ Return json object for flot chart
    """
    engine = create_engine('sqlite:///../data/'+ str(meterId) + '.db', echo=True)
    conn = engine.connect()

    query = """SELECT DATE_M, Ch1
    FROM INTERVAL_READINGS
    WHERE DATE_M >= DATE(:x)
    AND DATE_M < DATE(:y)
    ORDER BY DATE_M ASC
    """

    s = text(query)
    data = conn.execute(s, x=start_date, y=end_date).fetchall()

    chartdata = {}
    chartdata['label'] = 'Energy Profile'
    chartdata['consumption'] = []

    for row in data:
        dTime = arrow.get(row[0])
        ts = int(dTime.timestamp * 1000)
        chartdata['consumption'].append([ts, row[1]])

    return chartdata
