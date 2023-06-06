from datetime import datetime 
from operator import attrgetter
import json
from micro_services.client import *
from itertools import groupby
from services.air_freight_rate.models.air_freight_rate import AirFreightRate

def get_air_freight_rate_suggestions(validity_start,validity_end,searched_origin_airport_id,searched_destination_airport_id,filters={}):
    validity_start = datetime.strptime(validity_start, '%Y-%m-%d')
    validity_end = datetime.strptime(validity_end, '%Y-%m-%d')

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

    air_freight_rates = get_air_freight_rates(filters, searched_origin_airport_id, searched_destination_airport_id, validity_start)
    
    grouped_rates = get_grouped_rates(air_freight_rates, validity_start, validity_end)

    air_freight_rate_ids = [t['id'] for t in list(filter(None,grouped_rates.values()))]

    return { 'list': air_freight_rate_ids }

def get_air_freight_rates(filters,searched_origin_airport_id,searched_destination_airport_id,validity_start,validity_end):
    query = AirFreightRate.select()
    if filters:
        for key in filters:
            query = query.where(attrgetter(key)(AirFreightRate) == filters[key])

    air_freight_query = query.where(~AirFreightRate.rate_not_available_entry, AirFreightRate.origin_airport_id != searched_origin_airport_id, AirFreightRate.destination_airport_id != searched_destination_airport_id, AirFreightRate.last_rate_available_date >= max([validity_start, datetime.now()]))
    air_freight_rates = list(air_freight_query.dicts())
    return air_freight_rates

def get_grouped_rates(air_freight_rates,validity_start,validity_end):
    groupings = {}
    sorted_rates = sorted(air_freight_rates, key=lambda t: (t['origin_airport_id'], t['destination_airport_id']))
    for (origin, dest), group in groupby(sorted_rates, key=lambda t: (t['origin_airport_id'], t['destination_airport_id'])):
        groupings[(origin, dest)] = list(group)

    min_rate_groupings = {}

    for key,rates in groupings.items():
        for rate in rates:  
            validities = [t for t in rate['validities'] if (datetime.strptime(t['validity_end'],'%Y-%m-%d') >= max([validity_start, datetime.now()])) and (datetime.strptime(t['validity_start'],'%Y-%m-%d') <= validity_end) or (datetime.strptime(t['validity_start'],'%Y-%m-%d') >= validity_end)]
            min_validity = sorted(validities, key = lambda t: common.get_money_exchange_for_fcl({'price': t['price'], 'from_currency': t['currency'], 'to_currency': 'INR'})['price'])[0]
            rate['price'] = min_validity.get('price')
            rate['currency'] = min_validity.get('currency')
        min_rate = sorted([t for t in rates if t.get('price')], key = lambda t: common.get_money_exchange_for_fcl({'price': t['price'], 'from_currency': t['currency'], 'to_currency': 'INR'})['price'])[0]
        min_rate_groupings[key] = min_rate

    return min_rate_groupings
