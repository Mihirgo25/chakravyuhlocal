from services.fcl_freight_rate.models.fcl_freight_rate_local_agent import FclFreightRateLocalAgent
from fastapi.encoders import jsonable_encoder
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
from math import ceil
import json

possible_direct_filters = ['service_provider_id', 'trade_type', 'status', 'location_id']
possible_indirect_filters = ['location_ids']

def list_fcl_freight_rate_local_agents(filters = {}, page_limit = 10, page = 1, sort_by = 'updated_at', sort_type = 'desc', pagination_data_required = True):
    query = get_query(sort_by, sort_type)

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, FclFreightRateLocalAgent)
        query = apply_indirect_filters(query, indirect_filters)

    pagination_data = get_pagination_data(query, page, page_limit, pagination_data_required)
    query = query.paginate(page, page_limit)
    data = jsonable_encoder(list(query.dicts()))

    return {'list': data } | (pagination_data)

def get_query(sort_by, sort_type):
    query = FclFreightRateLocalAgent.select().order_by(eval('FclFreightRateLocalAgent.{}.{}()'.format(sort_by,sort_type)))
    return query

def get_pagination_data(query, page, page_limit, pagination_data_required):
    if not pagination_data_required:
        return {} 
        
    total_count = query.count()
    params = {
      'page': page,
      'total': ceil(total_count/page_limit),
      'total_count': total_count,
      'page_limit': page_limit
    }
    return params

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query
 
def apply_location_ids_filter(query, filters):
    return query.where(FclFreightRateLocalAgent.location_ids.contains(filters['location_ids']))
