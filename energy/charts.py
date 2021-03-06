import arrow
from .models import Energy
from .usage import get_energy_data, convert_wh_to_w, get_power_data
from .tariff import DailyUsage


def get_energy_chart_data(meter_id, start_date, end_date):
    """ Return json object for flot chart
    """
    chartdata = {}
    chartdata['label'] = 'Energy Profile'
    chartdata['consumption'] = []

    for r in get_energy_data(meter_id, start_date, end_date):
        dTime = arrow.get(r.reading_date)
        ts = int(dTime.timestamp * 1000)
        impWh = r.imp
        chartdata['consumption'].append([ts, impWh])

    chartdata['power'] = []
    for r in get_power_data(meter_id, start_date, end_date):
        dTime = arrow.get(r[0])
        ts = int(dTime.timestamp * 1000)
        ts = ts - (1000 * 60 * 30)  # Offset 30 mins so steps line up properly on chart
        impW = r[1]
        chartdata['power'].append([ts, impW])

    # Finally add one more point to finish the step increment
    if ts:
        ts = ts + (1000 * 60 * 30)  # Offset 30 mins so steps line up properly on chart
        chartdata['power'].append([ts, impW])

    return chartdata


def get_daily_chart_data(meter_id, start_date, end_date):
    """ Return json object for flot chart
    """
    chartdata = {}
    chartdata['label'] = 'Daily Usage'
    chartdata['consumption'] = []

    du = DailyUsage(meter_id, start_date, end_date)
    for day in du.daily_usage.keys():
        dTime = arrow.get(day).replace(days=+1)
        ts = int(dTime.timestamp * 1000)
        usage = du.daily_usage[day].consumption_total / 1000
        chartdata['consumption'].append([ts, usage])

    return chartdata
