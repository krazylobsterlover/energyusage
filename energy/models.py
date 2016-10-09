import sqlite3
import arrow


def get_energy_chart_data(meterId, start_date="2016-09-01",
                          end_date="2016-10-01"):
    """ Return json object for flot chart
    """

    conn = sqlite3.connect('../data/' + str(meterId) + '.db')
    c = conn.cursor()
    query = """SELECT DATE_M, Ch1
FROM INTERVAL_READINGS
WHERE DATE_M >= DATE(?)
AND DATE_M < DATE(?)
ORDER BY DATE_M ASC
"""
    c.execute(query, [start_date, end_date])
    header = [h[0] for h in c.description]
    data = c.fetchall()
    c.close()
    conn.close()

    chartdata = {}
    chartdata['label'] = 'Energy Profile'
    chartdata['consumption'] = []

    for row in data:
        dTime = arrow.get(row[0])
        ts = int(dTime.timestamp * 1000)
        chartdata['consumption'].append([ts, row[1]])

    return chartdata
