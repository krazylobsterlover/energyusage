import arrow
import datetime
from .models import Energy

METER_SERVICES_CHARGE = 8.94  # cents per day


class GeneralSupplyTariff(object):
    """ Used to calculate the costs of a general supply tariff
    """

    def __init__(self, meter_id):
        self.meter_id = meter_id
        self.daily_meter_services_charge = METER_SERVICES_CHARGE
        self.daily_supply_charge = 98.529  # cents per day
        self.consumption_rate = 27.071  # cents per kWh

    def calculate_bill(self, start_date, end_date):
        """ Calculate charges for specified period
        """
        num_days = (end_date - start_date).days
        self.meter_services_charge = self.daily_meter_services_charge * num_days
        self.supply_charge = self.daily_supply_charge * num_days
        self.consumption_kWh = 0
        for r in get_energy_data(self.meter_id, start_date, end_date):
            impWh = r.imp
            self.consumption_kWh += impWh / 1000  # charge is in kWh
        self.consumption_charge = self.consumption_rate * self.consumption_kWh

        self.total_cost = self.meter_services_charge + self.supply_charge + self.consumption_charge
        return self.total_cost


class TimeofUseTariff(object):
    """ Used to calculate the costs of a time of use tariff
    """

    def __init__(self, meter_id):
        self.meter_id = meter_id
        self.daily_meter_services_charge = METER_SERVICES_CHARGE
        self.daily_supply_charge = 111.437  # cents per day
        self.consumption_rate_peak = 61.452  # cents per kWh
        self.consumption_rate_offpeak = 21.845  # cents per kWh

    def calculate_bill(self, start_date, end_date):
        """ Calculate charges for specified period
        """
        num_days = (end_date - start_date).days
        self.meter_services_charge = self.daily_meter_services_charge * num_days
        self.supply_charge = self.daily_supply_charge * num_days
        self.peak_consumption_kWh = 0
        self.offpeak_consumption_kWh = 0
        for r in get_energy_data(self.meter_id, start_date, end_date):
            dTime = arrow.get(r.reading_date)
            impWh = r.imp
            if in_peak_period(dTime):
                self.peak_consumption_kWh += impWh / 1000  # charge is in kWh
            else:
                self.offpeak_consumption_kWh += impWh / 1000  # charge is in kWh

        self.peak_consumption_charge = self.consumption_rate_peak * self.peak_consumption_kWh
        self.offpeak_consumption_charge = self.consumption_rate_offpeak * self.offpeak_consumption_kWh

        self.total_cost = self.meter_services_charge + self.supply_charge + self.peak_consumption_charge + self.offpeak_consumption_charge
        return self.total_cost


def in_peak_period(reading_date):
    """ Deterime if reading is in peak period
    """
    d = arrow.get(reading_date)
    if d.month in [12,1,2]:
        peak_month = True
    else:
        peak_month = False
    if datetime.time(15, 0, 0) < d.time() < datetime.time(21, 1, 0):
        peak_time = True
    else:
        peak_time = False
    if peak_time and peak_month:
        return True
    else:
        return False


def convert_wh_to_w(Wh, hours=0.5):
    """ Find average W for the period, specified in hours
    """
    return Wh/hours


def get_energy_data(meter_id, start_date, end_date):
    """ Get energy data for a meter
    """
    readings = Energy.query.filter(Energy.user_id==meter_id)
    readings = readings.filter(Energy.reading_date>=start_date)
    readings = readings.filter(Energy.reading_date<=end_date).all()
    return readings


def get_total_consumption(meter_id, start_date, end_date):
    for r in get_energy_data(meter_id, start_date, end_date):
        dTime = arrow.get(r.reading_date)
        ts = int(dTime.timestamp * 1000)
        impWh = r.imp
        chartdata['consumption'].append([ts, impWh])
