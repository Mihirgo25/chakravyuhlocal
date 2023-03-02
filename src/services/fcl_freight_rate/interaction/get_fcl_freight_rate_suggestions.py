from services.fcl_freight_rate.models.fcl_freight_rates import FclFreightRate
from rails_client import client
from datetime import datetime
from itertools import groupby

def get_fcl_freight_rate_suggestions(filters, searched_origin_port_id, searched_destination_port_id, fcl_freight_rates, validity_start, validity_end):
    fcl_freight_rates = get_fcl_freight_rates(filters, searched_origin_port_id, searched_destination_port_id)

    grouped_rates = get_grouped_rates(fcl_freight_rates, validity_start, validity_end)

    fcl_freight_rate_ids = [t['id'] for t in filter(None,grouped_rates.values())]

    return { 'list': fcl_freight_rate_ids }

def get_fcl_freight_rates(filters, searched_origin_port_id, searched_destination_port_id, validity_start):
    fcl_freight_rates = FclFreightRate.select().where(**filters).where(FclFreightRate.rate_not_available_entry == False).where(FclFreightRate.last_rate_available_date >= max([datetime.strptime(validity_start, '%Y-%m-%d'), datetime.now()]))
    fcl_freight_rates = [rate for rate in fcl_freight_rates if rate['origin_port_id'] != searched_origin_port_id and rate['destination_port_id'] != searched_destination_port_id]
    return fcl_freight_rates

def get_grouped_rates(fcl_freight_rates, validity_start, validity_end):
    groupings = {}
    sorted_rates = sorted(fcl_freight_rates, key=lambda t: (t['origin_port_id'], t['destination_port_id']))
    for (origin, dest), group in groupby(sorted_rates, key=lambda t: (t['origin_port_id'], t['destination_port_id'])):
        groupings[(origin, dest)] = list(group)

    min_rate_groupings = {}
    
    for key, rates in groupings.items():
        for rate in rates: 
            validities = [t for t in rate['validities'] if datetime.strptime(t['validity_end'],'%Y-%m-%d') >= max([datetime.strptime(validity_start,'%Y-%m-%d'), datetime.now()]) and (datetime.strptime(t['validity_start'], '%Y-%m-%d') <= datetime.strptime(validity_end, '%Y-%m-%d') or datetime.strptime(t['validity_start'], '%Y-%m-%d') >= datetime.strptime(validity_end, '%Y-%m-%d'))]
            min_validity = sorted(validities, lambda t: client.ruby.get_money_exchange_for_fcl({'price': t['price'], 'from_currency': t['currency'], 'to_currency': 'INR'})['price'])[0]
            rate['price'] = min_validity.get('price')
            rate['currency'] = min_validity.get('currency')
        min_rate = sorted([t for t in rates if t['price']], lambda t: client.ruby.get_money_exchange_for_fcl({'price': t['price'], 'from_currency': t['currency'], 'to_currency': 'INR'})['price'])[0]
        min_rate_groupings[key] = min_rate

    return min_rate_groupings