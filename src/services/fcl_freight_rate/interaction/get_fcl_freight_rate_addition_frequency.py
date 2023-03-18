from datetime import datetime
from operator import attrgetter
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from services.fcl_freight_rate.helpers.find_or_initialize import apply_direct_filters
from peewee import JOIN, fn, SQL
import json

possible_direct_filters = ['origin_location_ids', 'destination_location_ids']

possible_indirect_filters = ['procured_by_id']

def get_fcl_freight_rate_addition_frequency(filters, sort_type, group_by):
    query = FclFreightRate.select().where(FclFreightRate.updated_at >= datetime.now().date().replace(year=datetime.now().year-1))

    if filters and type(filters) != dict:
      filters = json.loads(filters)
      query = apply_direct_filters(query, filters, possible_direct_filters, FclFreightRate)
      query = apply_indirect_filters(query, filters)

      data = get_data(query, sort_type, group_by)
      return data

def apply_indirect_filters(query, filters):
  for key in filters:
    if key in possible_indirect_filters:
      apply_filter_function = f'apply_{key}_filter'
      query = eval(f'{apply_filter_function}(query, filters)')
  return query

def get_data(query, group_by, sort_type):
    # return query.select(fn.COUNT(SQL('*')).alias('count_all')).group("date_trunc('#{self.group_by}',fcl_freight_rates.updated_at)").order_by(eval(f'fn.date_trunc_{group_by}_fcl_freight_rates.updated_at.{sort_type}()'))
    return (query.select(fn.COUNT(SQL('*')).alias('count_all'), fn.date_trunc(f'{group_by}', FclFreightRate.updated_at).alias(f'date_trunc_{group_by}_fcl_freight_rates_updated_at')
        ).group_by(fn.date_trunc(f'{group_by}', FclFreightRate.updated_at)
        ).order_by(eval(f"fn.date_trunc('{group_by}', FclFreightRate.updated_at).{sort_type}()")))

def apply_procured_by_id_filter(query, filters):
    return query.join(FclFreightRateAudit, JOIN.INNER, on = (FclFreightRateAudit.object_id == FclFreightRate.id)).where(FclFreightRateAudit.object_type == 'FclFreightRate', FclFreightRateAudit.procured_by_id == filters['procured_by_id'])