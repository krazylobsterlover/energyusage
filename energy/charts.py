import arrow
from .models import Energy
from .tariff import get_energy_data, convert_wh_to_w


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


def get_power_data(meter_id, start_date, end_date):
    """ Get 30 min power data for a meter
    """
    power = {}
    for r in get_energy_data(meter_id, start_date, end_date):
        rd = arrow.get(r.reading_date)
        imp = r.imp

        # Round up to nearest 30 min interval
        if rd.minute == 0:
            pass # Nothing to do
        elif rd.minute > 30:
            rd = rd.replace(minute=0)
            rd = rd.replace(hours=+1)
        else:
            rd = rd.replace(minute=30)

        # Increment dictionary value
        if rd not in power:
            power[rd] = imp
        else:
            power[rd] += imp

    for key in sorted(power.keys()):
        impW = convert_wh_to_w(power[key], hours=0.5)
        yield [key, impW]