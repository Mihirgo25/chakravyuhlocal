from services.chakravyuh.models.fcl_freight_rate_estimation_audit import FclFreightRateEstimationAudit
from libs.json_encoder import json_encoder
from math import ceil
from datetime import datetime
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
import json

possible_direct_filters = ['object_id']

possible_indirect_filters = ['created_at_greater_than', 'created_at_less_than']

def apply_created_at_greater_than_filter(query, filters):
  query = query.where(FclFreightRateEstimationAudit.created_at.cast('date') >= datetime.fromisoformat(filters['created_at_greater_than']).date())
  return query


def apply_created_at_less_than_filter(query, filters):
  query = query.where(FclFreightRateEstimationAudit.created_at.cast('date') <= datetime.fromisoformat(filters['created_at_less_than']).date())
  return query

def apply_indirect_filters(query, filters):
  for key in filters:
    apply_filter_function = f'apply_{key}_filter'
    query = eval(f'{apply_filter_function}(query, filters)')
  return query

def list_fcl_freight_rate_estimation_trends(filters, page_limit, page, sort_by, sort_type):
  query = FclFreightRateEstimationAudit.select(
      FclFreightRateEstimationAudit.data,
      FclFreightRateEstimationAudit.id,
      FclFreightRateEstimationAudit.created_at
  ).order_by(eval('FclFreightRateEstimationAudit.{}.{}()'.format(sort_by,sort_type)))

  if filters:
    if type(filters) != dict:
      filters = json.loads(filters)

    direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
    query = get_filters(direct_filters, query, FclFreightRateEstimationAudit)
    query = apply_indirect_filters(query, indirect_filters)

  pagination_data = get_pagination_data(query, page, page_limit)
  query = query.paginate(page,page_limit)

  data = get_data(query)

  return { 'list': data } | (pagination_data)


def get_data(query):
    data = json_encoder(list(query.dicts()))


    for item in data:
        estimation_data = item['data']
        line_items = estimation_data.get('line_items')
        actual_line_items = estimation_data.get('actual_line_items')

        freight_lineitem = {}

        actual_lineitem = {}

        if line_items:
            for line_item in line_items:
                if line_item['code'] == 'BAS':
                    freight_lineitem = line_item
                    break
        
        if actual_line_items:
            for line_item in actual_line_items:
                if line_item['code'] == 'BAS':
                    actual_lineitem = line_item
                    break
        
        item['tf'] = freight_lineitem
        item['actual_line_item'] = actual_lineitem 
        # item['created_at'] = str(datetime.fromisoformat(item['created_at']).date())

        del item['data']
    
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