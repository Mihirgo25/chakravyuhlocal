import concurrent.futures
from services.fcl_freight_rate.models.fcl_freight_rate_local_agent import FclFreightRateLocalAgent
from playhouse.shortcuts import model_to_dict
from services.fcl_freight_rate.helpers.find_or_initialize import apply_direct_filters
from math import ceil
import json
from micro_services.client import common

possible_direct_filters = ['service_provider_id', 'trade_type', 'status', 'location_id']
possible_indirect_filters = ['location_ids']

def list_fcl_freight_rate_local_agents(filters = {}, page_limit = 10, page = 1, sort_by = 'updated_at', sort_type = 'desc', pagination_data_required = True):
    query = get_query(sort_by, sort_type, page, page_limit)

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)
        query = apply_direct_filters(query, filters, possible_direct_filters, FclFreightRateLocalAgent)
        query = apply_indirect_filters(query, filters)



    data = get_data(query)
    pagination_data = get_pagination_data(query, page, page_limit, pagination_data_required)

    return {'list': data } | (pagination_data)

def get_query(sort_by, sort_type, page, page_limit):
    query = FclFreightRateLocalAgent.select().order_by(eval('FclFreightRateLocalAgent.{}.{}()'.format(sort_by,sort_type))).paginate(page, page_limit)
    return query

def get_data(query):
    data = [model_to_dict(item) for item in query.execute()]

    return data

def get_pagination_data(data, page, page_limit, pagination_data_required):
    if not pagination_data_required:
        return {} 

    params = {
      'page': page,
      'total': ceil(len(data)/page_limit),
      'total_count': len(data),
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
