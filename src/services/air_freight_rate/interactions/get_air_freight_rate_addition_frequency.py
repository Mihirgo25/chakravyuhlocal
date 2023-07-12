from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from libs.get_applicable_filters import get_applicable_filters
from datetime import datetime, timedelta
from libs.get_filters import get_filters
from fastapi.encoders import jsonable_encoder
from peewee import fn, SQL
import json

possible_direct_filters = ['origin_airport_id', 'destination_airport_id']
possible_indirect_filters = ['procured_by_id']

def get_air_freight_rate_addition_frequency(group_by, filters = {}, sort_type = 'desc'):
    query = get_query()
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)        
        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
        query = apply_indirect_filters(query,indirect_filters)
        query = get_filters(direct_filters, query, AirFreightRate)

    
    data  = get_data(query,group_by,sort_type)
    
    return data

def get_query():
    query = AirFreightRate.select().where(AirFreightRate.updated_at >= datetime.now().date().replace(year=datetime.now().year-1))
    return query

def get_data(query,group_by,sort_type ):
    data = (query.select(fn.COUNT(SQL('*')).alias('count_all'), fn.date_trunc(group_by, AirFreightRate.updated_at).alias(f'date_trunc_{group_by}_air_freight_rates_temp_updated_at')
        ).group_by(fn.date_trunc(group_by, AirFreightRate.updated_at)
        ).order_by(eval("fn.date_trunc('{}', AirFreightRate.updated_at).{}()".format(group_by,sort_type))))
    return jsonable_encoder(list(data.dicts()))

  

def apply_indirect_filters(query,filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query

