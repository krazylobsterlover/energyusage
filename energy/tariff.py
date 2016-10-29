import arrow
import datetime
import statistics
from .models import Energy

METER_SERVICES_CHARGE = 8.94  # cents/day


class GeneralSupplyTariff(object):
    """ Used to calculate the costs of a general supply tariff
    """

    def __init__(self, meter_id):
        self.meter_id = meter_id
        self.daily_meter_services_charge = METER_SERVICES_CHARGE
        self.daily_supply_charge = 98.529  # cents/day
        self.consumption_rate = 27.071  # cents/kWh

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
        self.daily_supply_charge = 111.437  # cents/day
        self.consumption_rate_peak = 61.452  # cents/kWh
        self.consumption_rate_offpeak = 21.845  # cents/kWh

    def calculate_bill(self, start_date, end_date):
        """ Calculate charges for specified period
        """
        num_days = (end_date - start_date).days
        self.meter_services_charge = self.daily_meter_services_charge * num_days
        self.supply_charge = self.daily_supply_charge * num_days
        self.peak_consumption_kWh = 0
        self.offpeak_consumption_kWh = 0
        for r in get_energy_data(self.meter_id, start_date, end_date):
            reading_date = arrow.get(r.reading_date)
            impWh = r.imp
            if in_peak_period(reading_date):
                self.peak_consumption_kWh += impWh / 1000  # charge is in kWh
            else:
                self.offpeak_consumption_kWh += impWh / 1000  # charge is in kWh

        self.peak_consumption_charge = self.consumption_rate_peak * self.peak_consumption_kWh
        self.offpeak_consumption_charge = self.consumption_rate_offpeak * self.offpeak_consumption_kWh

        self.total_cost = self.meter_services_charge + self.supply_charge + self.peak_consumption_charge + self.offpeak_consumption_charge
        return self.total_cost


class DemandTariff(object):
    """ Used to calculate the costs of a time of use demand tariff
    """

    def __init__(self, meter_id):
        self.meter_id = meter_id
        self.daily_meter_services_charge = METER_SERVICES_CHARGE
        self.daily_supply_charge = 66.5654  # cents/day
        self.consumption_rate = 16.4824  # cents/kWh
        self.demand_charge_peak = 67.969  # $/kw/mth
        self.demand_charge_offpeak = 12.3838  # $/kw/mth

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


        # The  peak  demand  charge  will  be  applied to  average kW
        # demand  calculated  for  the  52  half  hour  periods  each
        # month (i.e. 13 half hour intervals in each demand window
        # on the 4 highest demand days)
        peak_days = dict()
        for r in get_power_data(self.meter_id, start_date, end_date):
            reading_date = arrow.get(r[0])
            impW = r[1]
            if in_peak_time(reading_date):
                day = reading_date.format('YYYY-MM-DD')
                if day in peak_days.keys():
                    peak_days[day].append(impW)
                else:
                    peak_days[day] = [impW]

        # Calculate daily peak
        for day in peak_days:
            daily_peak = max(peak_days[day])
            peak_days[day] = (daily_peak, peak_days[day])

        # Sort and get top 4 days
        # For now lets just get first 4 days
        top_four_days = []
        for i, day in enumerate(peak_days.keys()):
            if i < 4:
                top_four_days.append(day)

        # Calculate average demand
        demand_window = []
        for day in top_four_days:
            for reading in peak_days[day][1]:
                demand_window.append(reading)
        if demand_window:
            self.peak_demand_kW = statistics.mean(demand_window)/1000
        else:
            self.peak_demand_kW = 0

        # Determine rate depending on if peak season
        try:
            peak_day = top_four_days[0]
        except IndexError:
            peak_day = arrow.get(start_date).format('YYYY-MM-DD')
        self.peak_season = in_peak_season(peak_day)
        if self.peak_season:
            self.demand_charge = self.peak_demand_kW * self.demand_charge_peak
        else:
            # The  off  peak  demand  quantity  is  subject  to  a  minimum chargeable  demand  of  3kW
            if self.peak_demand_kW < 3:
                self.peak_demand_kW = 3
            self.demand_charge = self.peak_demand_kW * self.demand_charge_offpeak * 100  # in cents

        # Daily Calculation should scale demand charge
        print(num_days)
        if num_days < 2:
            self.demand_charge = self.demand_charge / 30
        self.total_cost = self.meter_services_charge + self.supply_charge + self.consumption_charge + self.demand_charge
        return self.total_cost


def in_peak_period(reading_date):
    """ Deterime if reading is in peak period
    """
    if in_peak_season(reading_date) and in_peak_time(reading_date):
        return True
    else:
        return False


def in_peak_season(reading_date):
    """ In  summer  months
        Dec, Jan, Feb
    """
    d = arrow.get(reading_date)
    if d.month in [12,1,2]:
        return True
    else:
        return False


def in_peak_time(reading_date):
    """ In  the  daily  peak  demand  window
        between 3.00 pm and 9.30 pm
    """
    d = arrow.get(reading_date)
    if datetime.time(15, 0, 0) < d.time() < datetime.time(21, 1, 0):
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
