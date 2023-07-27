from datetime import datetime
from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
from libs.json_encoder import json_encoder
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
from peewee import fn, SQL
import json

possible_direct_filters = ['procured_by_id', 'origin_location_ids', 'destination_location_ids']

possible_indirect_filters = []

def get_haulage_freight_rate_addition_frequency(group_by, filters = {}, sort_type = 'desc'):
    """
    Get Haulage Freight Rate Addition Frequency
    Response Format:
        returns a integer of total frequency count that is used in partner user rate stats
    """
    query = HaulageFreightRate.select().where(HaulageFreightRate.updated_at >= datetime.now().date().replace(year=datetime.now().year-1))
    if filters:
      if type(filters) != dict:
        filters = json.loads(filters)
        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, HaulageFreightRate)
        query = apply_indirect_filters(query, indirect_filters)

    data = get_data(query, sort_type, group_by)
    return data

def get_data(query, sort_type, group_by):
    data = (query.select(fn.COUNT(SQL('*')).alias('count_all'), fn.date_trunc(f'{group_by}', HaulageFreightRate.updated_at).alias(f'date_trunc_{group_by}_haulage_freight_rates_temp_updated_at')
        ).group_by(fn.date_trunc(f'{group_by}', HaulageFreightRate.updated_at)
        ).order_by(eval(f"fn.date_trunc('{group_by}', HaulageFreightRate.updated_at).{sort_type}()")))
    return json_encoder(list(data.dicts()))[0]['count_all']

def apply_indirect_filters(query, filters):
  for key in filters:
    if key in possible_indirect_filters:
      apply_filter_function = f'apply_{key}_filter'
      query = eval(f'{apply_filter_function}(query, filters)')
  return query

def apply_origin_location_ids_filter(query, filters):
   query = query.where(HaulageFreightRate.origin_location_ids.contains(filters['origin_location_ids']))
   return query

def apply_destination_location_ids_filter(query, filters):
   query = query.where(HaulageFreightRate.destination_location_ids.contains(filters['destination_location_ids']))
   return query


