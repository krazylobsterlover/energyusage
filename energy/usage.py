import arrow
import datetime
import statistics
from .models import Energy
from . import tariff_config as tc


class UsageStats(object):
    """ Get the energy stats for a time period, usually a single day
    """

    def __init__(self, usage):

        self.consumption_peak = 0
        self.consumption_offpeak = 0
        self.demand_list = []

        for r in usage:
            reading_date = arrow.get(r[0])
            usage_W = r[1]
            usage_Wh = convert_w_to_wh(usage_W, hours=0.5)

            if in_peak_period(reading_date):
                self.consumption_peak += usage_Wh
            else:
                self.consumption_offpeak += usage_Wh

            if in_peak_time(reading_date):
                self.demand_list.append(usage_W)

        self.demand_abs_peak = 0
        self.demand_avg_peak = 0
        if self.demand_list:
            self.demand_abs_peak = max(self.demand_list)
            self.demand_avg_peak = statistics.mean(self.demand_list)
        self.consumption_total = self.consumption_peak + self.consumption_offpeak


def get_power_data(meter_id, start_date, end_date):
    """ Get 30 min power data for a meter
    """
    power = {}
    for r in get_energy_data(meter_id, start_date, end_date):
        rd = arrow.get(r.reading_date)
        interval = r.interval
        imp = r.imp
        if not imp:  # If null
            imp = 0

        # Round up to nearest 30 min interval
        if rd.minute == 0:
            pass  # Nothing to do
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


def get_energy_data(meter_id, start_date, end_date):
    """ Get energy data for a meter
    """
    readings = Energy.query.filter(Energy.user_id == meter_id)
    readings = readings.filter(Energy.reading_date >= start_date)
    readings = readings.filter(Energy.reading_date <= end_date).all()
    return readings


def in_peak_period(reading_date):
    """ Deterime if reading is in peak period
    """
    if in_peak_season(reading_date, peak_months=tc.PEAK_MONTHS):
        if in_peak_time(reading_date, peak_start=tc.PEAK_WINDOW_START, peak_end=tc.PEAK_WINDOW_END):
            return True
        else:
            return False
    else:
        return False


def in_peak_season(reading_date, peak_months=[12, 1, 2]):
    """ Determine if date is inside the peak season

        Defaults to summer months of Dec, Jan, Feb
    """
    d = arrow.get(reading_date)
    if d.month in tc.PEAK_MONTHS:
        return True
    else:
        return False


def in_peak_time(reading_date,
                 peak_start=datetime.time(15, 0, 0),
                 peak_end=datetime.time(21, 1, 0)
                 ):
    """ Determine if in  the  daily  peak  demand  window

        Defaults to between 3.00 pm and 9.30 pm
    """
    d = arrow.get(reading_date)
    if peak_start < d.time() <= peak_end:
        return True
    else:
        return False


def convert_wh_to_w(Wh, hours=0.5):
    """ Find average W for the period, specified in hours
    """
    return Wh / hours


def convert_w_to_wh(W, hours=0.5):
    """ Find average W for the period, specified in hours
    """
    return W * hours
