from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from operator import attrgetter
from micro_services.client import *
from datetime import datetime
from itertools import groupby
from playhouse.shortcuts import model_to_dict
import json

def get_fcl_freight_rate_suggestions(validity_start, validity_end, searched_origin_port_id, searched_destination_port_id, filters = {}):
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

    validity_start = datetime.strptime(validity_start, '%Y-%m-%d')
    validity_end = datetime.strptime(validity_end, '%Y-%m-%d')
    
    fcl_freight_rates = get_fcl_freight_rates(filters, searched_origin_port_id, searched_destination_port_id, validity_start)

    grouped_rates = get_grouped_rates(fcl_freight_rates, validity_start, validity_end)

    fcl_freight_rate_ids = [t['id'] for t in list(filter(None,grouped_rates.values()))]

    return { 'list': fcl_freight_rate_ids }

def get_fcl_freight_rates(filters, searched_origin_port_id, searched_destination_port_id, validity_start):
    query = FclFreightRate.select()
    for key in filters:
        query = query.where(attrgetter(key)(FclFreightRate) == filters[key])

    fcl_freight_query = query.where(FclFreightRate.rate_not_available_entry == False, FclFreightRate.origin_port_id != searched_origin_port_id, FclFreightRate.destination_port_id != searched_destination_port_id, FclFreightRate.last_rate_available_date >= max([validity_start, datetime.now()]))
    fcl_freight_rates = [model_to_dict(item) for item in fcl_freight_query.execute()]
    return fcl_freight_rates

def get_grouped_rates(fcl_freight_rates, validity_start, validity_end):
    groupings = {}
    sorted_rates = sorted(fcl_freight_rates, key=lambda t: (t['origin_port_id'], t['destination_port_id']))
    for (origin, dest), group in groupby(sorted_rates, key=lambda t: (t['origin_port_id'], t['destination_port_id'])):
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