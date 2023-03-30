from services.fcl_freight_rate.models.fcl_freight_rate_seasonal_surcharge import FclFreightRateSeasonalSurcharge
from fastapi.encoders import jsonable_encoder
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
from math import ceil
import json

possible_direct_filters = ['origin_port_id', 'origin_country_id', 'origin_trade_id', 'origin_continent_id', 'destination_port_id', 'destination_country_id', 'destination_trade_id', 'destination_continent_id', 'shipping_line_id', 'service_provider_id', 'container_size', 'container_type', 'code', 'origin_location_id', 'destination_location_id']
possible_indirect_filters = []

def list_fcl_freight_rate_seasonal_surcharges(filters = {}, page_limit = 10, page = 1, pagination_data_required = True):
    query = get_query(page, page_limit)
    if filters:
      if type(filters) != dict:
        filters = json.loads(filters)

      direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)

      query = get_filters(direct_filters, query, FclFreightRateSeasonalSurcharge)
      query = apply_indirect_filters(query, indirect_filters)
    
    data = jsonable_encoder(list(query.dicts()))
    pagination_data = get_pagination_data(query, page, page_limit, pagination_data_required)
    return { 'list': data } | (pagination_data)

def get_query(page, page_limit):
    query = FclFreightRateSeasonalSurcharge.select(
            FclFreightRateSeasonalSurcharge.id,
            FclFreightRateSeasonalSurcharge.origin_location_id,
            FclFreightRateSeasonalSurcharge.destination_location_id,
            FclFreightRateSeasonalSurcharge.shipping_line_id,
            FclFreightRateSeasonalSurcharge.service_provider_id,
            FclFreightRateSeasonalSurcharge.container_size,
            FclFreightRateSeasonalSurcharge.container_type,
            FclFreightRateSeasonalSurcharge.validity_start,
            FclFreightRateSeasonalSurcharge.validity_end,
            FclFreightRateSeasonalSurcharge.code,
            FclFreightRateSeasonalSurcharge.price,
            FclFreightRateSeasonalSurcharge.currency,
            FclFreightRateSeasonalSurcharge.remarks,
            FclFreightRateSeasonalSurcharge.shipping_line,
            FclFreightRateSeasonalSurcharge.origin_location,
            FclFreightRateSeasonalSurcharge.destination_location,
            FclFreightRateSeasonalSurcharge.service_provider
          ).order_by(FclFreightRateSeasonalSurcharge.updated_at.desc()).paginate(page, page_limit)
    return query

     
def get_pagination_data(data, page, page_limit, pagination_data_required):
  if not pagination_data_required:
    return {}

  pagination_data = {
    'page': page,
    'total': ceil(len(data)/page_limit),
    'total_count': len(data),
    'page_limit': page_limit
    }
  
  return pagination_data

def apply_indirect_filters(query, filters):
  for key in filters:
    if key in possible_indirect_filters:
      apply_filter_function = f'apply_{key}_filter'
      query = eval(f'{apply_filter_function}(query, filters)')
  return query