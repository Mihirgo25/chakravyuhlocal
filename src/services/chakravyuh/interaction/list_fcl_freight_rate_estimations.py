from services.chakravyuh.models.fcl_freight_rate_estimation import FclFreightRateEstimation
from fastapi.encoders import jsonable_encoder
from math import ceil
from datetime import datetime
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
import json

possible_direct_filters = ['id', 'origin_location_id', 'destination_location_id', 'origin_location_type', 'shipping_line_id', 'container_size', 'container_type']

possible_indirect_filters = ['created_at_greater_than', 'created_at_less_than']

def apply_created_at_greater_than_filter(query, filters):
  query = query.where(FclFreightRateEstimation.created_at.cast('date') >= datetime.fromisoformat(filters['created_at_greater_than']).date())
  return query


def apply_created_at_less_than_filter(query, filters):
  query = query.where(FclFreightRateEstimation.created_at.cast('date') <= datetime.fromisoformat(filters['created_at_less_than']).date())
  return query

def apply_indirect_filters(query, filters):
  for key in filters:
    apply_filter_function = f'apply_{key}_filter'
    query = eval(f'{apply_filter_function}(query, filters)')
  return query


def list_fcl_freight_rate_estimations(filters, page_limit, page, sort_by, sort_type):
  query = FclFreightRateEstimation.select().order_by(eval('FclFreightRateEstimation.{}.{}()'.format(sort_by,sort_type)))

  if filters:
    if type(filters) != dict:
      filters = json.loads(filters)

    direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
    query = get_filters(direct_filters, query, FclFreightRateEstimation)
    query = apply_indirect_filters(query, indirect_filters)

  pagination_data = get_pagination_data(query, page, page_limit)
  query = query.paginate(page,page_limit)

  data = get_data(query)

  return { 'list': data } | (pagination_data)


def get_data(query):
    data = jsonable_encoder(list(query.dicts()))


    for item in data:
        item['price'] = item['line_items'][0]
        del item['line_items']
    
    return data


def get_pagination_data(query, page, page_limit):
  total_count = query.count()
  
  pagination_data = {
    'page': page,
    'total': ceil(total_count/page_limit),
    'total_count': total_count,
    'page_limit': page_limit
    }
  
  return pagination_data