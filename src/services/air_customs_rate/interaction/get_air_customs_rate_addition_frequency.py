from services.air_customs_rate.models.air_customs_rate import AirCustomsRate
from datetime import datetime
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
import json
from peewee import fn, SQL
from fastapi.encoders import jsonable_encoder

possible_direct_filters = ['procured_by_id']

possible_indirect_filters = ['location_ids']

def get_air_customs_rate_addition_frequency(group_by, filters = {}, sort_type = 'desc'):
    query = get_query()
    if filters:
      if type(filters) != dict:
        filters = json.loads(filters)
      direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
      query = get_filters(direct_filters, query, AirCustomsRate)
      query = apply_indirect_filters(query, indirect_filters)

    data = get_data(query, sort_type, group_by)
    return data


def get_query():
    query = AirCustomsRate.select().where(AirCustomsRate.updated_at >= datetime.now().date().replace(year=datetime.now().year-1))
    return query

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query

def get_data(query, sort_type, group_by):
    data = (query.select(fn.COUNT(SQL('*')).alias('count_all'), fn.date_trunc(f'{group_by}', AirCustomsRate.updated_at).alias(f'date_trunc_{group_by}_air_customs_rates_updated_at')
        ).group_by(fn.date_trunc(f'{group_by}', AirCustomsRate.updated_at)
        ).order_by(eval(f"fn.date_trunc('{group_by}', AirCustomsRate.updated_at).{sort_type}()")))
    return jsonable_encoder(list(data.dicts()))

def apply_location_ids_filter(query, filters):
    location_ids = filters.get('location_ids')
    query = query.where(AirCustomsRate.location_ids.contains(location_ids))
    return query 