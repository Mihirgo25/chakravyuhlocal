from datetime import datetime 
from operator import attrgetter
import json
from micro_services.client import *
from itertools import groupby
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from libs.json_encoder import json_encoder
def get_air_freight_rate_suggestions(validity_start,validity_end,searched_origin_airport_id,searched_destination_airport_id,filters={}):
    validity_start = validity_start.date()
    validity_end = validity_end.date()

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

    air_freight_rates = get_air_freight_rates(filters, searched_origin_airport_id, searched_destination_airport_id, validity_start)
    
    grouped_rates = get_grouped_rates(air_freight_rates, validity_start, validity_end)

    return { 'list': list(filter(None,grouped_rates.values())) }

def get_air_freight_rates(filters,searched_origin_airport_id,searched_destination_airport_id,validity_start):
    query = AirFreightRate.select(AirFreightRate.id,AirFreightRate.validities,AirFreightRate.origin_airport_id,AirFreightRate.destination_airport_id)
    if filters:
        for key in filters:
            query = query.where(attrgetter(key)(AirFreightRate) == filters[key])
    air_freight_query = query.where(~AirFreightRate.rate_not_available_entry, AirFreightRate.origin_airport_id != searched_origin_airport_id, AirFreightRate.destination_airport_id != searched_destination_airport_id, AirFreightRate.last_rate_available_date >= max([validity_start, datetime.now().date()])).limit(1000)
    air_freight_rates = json_encoder(list(air_freight_query.dicts()))
    return air_freight_rates

def get_grouped_rates(air_freight_rates,validity_start,validity_end):
    groupings = {}
    
    for freight_rate in air_freight_rates:
        key = "{}:{}".format(freight_rate['origin_airport_id'],freight_rate['destination_airport_id'])
        if key in groupings.keys():
            groupings[key] = groupings[key] + [freight_rate]
        else:
            groupings[key] = [freight_rate]

    min_rate_groupings = {}

    for key,rates in groupings.items():
        min_price = 10000000
        min_rate = rates[0]
        for rate in rates: 
            key = "{}:{}".format(rate['origin_airport_id'],rate['destination_airport_id'])
            min_validity_price = 1000000
            for validity in rate['validities']:
                validity['validity_end'] = datetime.strptime(validity['validity_end'],'%Y-%M-%d').date()
                validity['validity_start'] = datetime.strptime(validity['validity_start'],'%Y-%M-%d').date()
                if validity['validity_end'] >= max(validity_start,datetime.now().date()) and (validity['validity_start'] <= validity_end or validity['validity_start'] >= validity_end):
                    if validity['currency']!='INR':
                        validity['min_price'] = common.get_money_exchange_for_fcl({'price': validity['min_price'], 'from_currency': validity['currency'], 'to_currency': 'INR'})['price']
                    min_validity_price = min(validity['min_price'],min_validity_price)
            if min_validity_price < min_price:
                min_rate = rate
                min_price = min_validity_price
            min_rate_groupings[key] = min_rate['id']
    return min_rate_groupings
