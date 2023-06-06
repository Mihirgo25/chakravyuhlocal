from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from libs.get_applicable_filters import get_applicable_filters
from datetime import datetime, timedelta
from fastapi.encoders import jsonable_encoder
from peewee import fn, SQL

possible_direct_filters = ['origin_airport_id', 'destination_airport_id']
possible_indirect_filters = ['procured_by_id']



def get_air_freight_rate_addition_frequency(group_by, filters = {}, sort_type = 'desc'):
    direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
    query = get_query()
    query = apply_indirect_filters(query,indirect_filters)
    
    data  = get_data(query,group_by,sort_type)
    
    return data

def get_query():
    query = AirFreightRate.select().where(AirFreightRate.updated_at >= datetime.now().date().replace(year=datetime.now().year-1))
    return query

def get_data(query,group_by,sort_type):
    data = (query.select(fn.COUNT(SQL('*')).alias('count_all'), fn.date_trunc(f'{group_by}', AirFreightRate.updated_at).alias(f'date_trunc_{group_by}_air_freight_rates_temp_updated_at')
        ).group_by(fn.date_trunc(f'{group_by}', AirFreightRate.updated_at)
        ).order_by(eval(f"fn.date_trunc('{group_by}', AirFreightRate.updated_at).{sort_type}()")))
    print(data)
    return jsonable_encoder(list(data.dicts()))
    # return 

  

def apply_indirect_filters(query,filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query

