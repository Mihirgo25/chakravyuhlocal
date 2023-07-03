from datetime import datetime
from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
from services.haulage_freight_rate.models.haulage_freight_rate_audit import HaulageFreightRateAudit
from fastapi.encoders import jsonable_encoder
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
from peewee import fn, SQL
import json

possible_direct_filters = ['origin_location_ids', 'destination_location_ids']

possible_indirect_filters = ['procured_by_id']

def get_haulage_freight_rate_addition_frequency(group_by, filters = {}, sort_type = 'desc'):
    query = HaulageFreightRate.select().where(HaulageFreightRate.updated_at >= datetime.now().date().replace(year=datetime.now().year-1))
    if filters:
      if type(filters) != dict:
        filters = json.loads(filters)
        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, HaulageFreightRate)
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
    data = (query.select(fn.COUNT(SQL('*')).alias('count_all'), fn.date_trunc(f'{group_by}', HaulageFreightRate.updated_at).alias(f'date_trunc_{group_by}_haulage_freight_rates_temp_updated_at')
        ).group_by(fn.date_trunc(f'{group_by}', HaulageFreightRate.updated_at)
        ).order_by(eval(f"fn.date_trunc('{group_by}', HaulageFreightRate.updated_at).{sort_type}()")))
    return jsonable_encoder(list(data.dicts()))

def apply_procured_by_id_filter(query, filters):
   query = query.join(HaulageFreightRateAudit, on=(HaulageFreightRateAudit.object_id == HaulageFreightRate.id)).where((HaulageFreightRateAudit.object_type == 'HaulageFreightRate') &
                        (HaulageFreightRate.procured_by_id == filters['procured_by_id']))
   return query