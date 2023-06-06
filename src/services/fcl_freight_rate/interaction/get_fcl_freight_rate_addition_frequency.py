from datetime import datetime
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from fastapi.encoders import jsonable_encoder
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
from peewee import fn, SQL
import json

possible_direct_filters = ['origin_location_ids', 'destination_location_ids']

possible_indirect_filters = ['procured_by_id']

def get_fcl_freight_rate_addition_frequency(group_by, filters = {}, sort_type = 'desc'):
    query = FclFreightRate.select().where(FclFreightRate.updated_at >= datetime.now().date().replace(year=datetime.now().year-1))

    if filters:
      if type(filters) != dict:
        filters = json.loads(filters)
        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, FclFreightRate)
        query = apply_indirect_filters(query, indirect_filters)

    data = get_data(query, sort_type, group_by)
    return data

def apply_indirect_filters(query, filters):
  for key in filters:
    if key in possible_indirect_filters:
      apply_filter_function = f'apply_{key}_filter'
      query = eval(f'{apply_filter_function}(query, filters)')
  return query

def get_data(query, sort_type, group_by):
    data = (query.select(fn.COUNT(SQL('*')).alias('count_all'), fn.date_trunc(f'{group_by}', FclFreightRate.updated_at).alias(f'date_trunc_{group_by}_fcl_freight_rates_temp_updated_at')
        ).group_by(fn.date_trunc(f'{group_by}', FclFreightRate.updated_at)
        ).order_by(eval(f"fn.date_trunc('{group_by}', FclFreightRate.updated_at).{sort_type}()")))
    print(data)
    return jsonable_encoder(list(data.dicts()))

def apply_procured_by_id_filter(query, filters):
    return query.where(FclFreightRate.procured_by_id == filters['procured_by_id'])