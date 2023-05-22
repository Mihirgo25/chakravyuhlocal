from datetime import datetime, timedelta
from math import ceil
from micro_services.client import common
import random
from configs.cogo_assured_rate_constants import *
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate

def get_suggested_cogo_assured_fcl_freight_rates(rate_param):
    data = add_suggested_validities(rate_param)

    return {'data' : data}

def add_suggested_validities(rate_param):
    rate_param['validities'] = [{
        'validity_start': datetime.now(), 
        'validity_end': datetime.now() + timedelta(days=(6 - datetime.now().weekday())),
        'price': rate_param['price'],
        'currency': rate_param['currency'],
        'line_items': [{
            'code': 'BAS',
            'unit': 'per_container',
            'price': rate_param['price'],
            'currency': rate_param['currency']
        }]
    }]

    deviation = ceil(float(rate_param['validities'][0]['price']) * 0.05)
    max_deviation = ceil(common.get_money_exchange_for_fcl({'from_currency': MAX_DEVIATION_CURRENCY, 'to_currency': rate_param['validities'][0]['currency'], 'price': MAX_DEVIATION_PRICE})['price'])

    max_deviation = (min(max_deviation, deviation) * -1)
    number_of_weeks = 4
    week_wise_deviation = ceil(max_deviation / number_of_weeks)

    for week in range(1,number_of_weeks+1):
        previous_validity = rate_param['validities'][-1]

        validity_start = previous_validity['validity_end'] + timedelta(days = 1)
        validity_end = validity_start + timedelta(days=(6 - validity_start.weekday()))

        deviation = random.randint(week_wise_deviation, week_wise_deviation+5)

        price = previous_validity['price'] + deviation

        rate_param['validities'].append({
            'validity_start' : validity_start,
            'validity_end' : validity_end,
            'price' : ceil(price),
            'currency': previous_validity['currency'],
            'line_items': [{
                'code': 'BAS',
                'unit': 'per_container',
                'price': price,
                'currency': previous_validity['currency']
            }]
        })

    return rate_param

def add_market_place():
    chunk_size = 5000  
    total_rows = FclFreightRate.select().count()
    total_chunks = (total_rows // chunk_size) + 1

    for chunk in range(total_chunks):
        offset = chunk * chunk_size
        subquery = FclFreightRate.select(FclFreightRate.id).where(FclFreightRate.rate_type == 'market_place').limit(chunk_size).offset(offset)
        query = FclFreightRate.update(init_key=FclFreightRate.init_key.concat(':market_place')).where(FclFreightRate.id.in_(subquery),FclFreightRate.init_key.endswith(':market_place') == False)
        print(query)
        query.execute()
    return {"message": "Market place added to init_key column for all rows."}