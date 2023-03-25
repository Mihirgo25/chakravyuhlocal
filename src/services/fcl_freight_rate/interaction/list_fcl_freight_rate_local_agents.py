import concurrent.futures
from services.fcl_freight_rate.models.fcl_freight_rate_local_agent import FclFreightRateLocalAgent
from playhouse.shortcuts import model_to_dict
from services.fcl_freight_rate.helpers.find_or_initialize import apply_direct_filters
from math import ceil
import json
from micro_services.client import common

possible_direct_filters = ['service_provider_id', 'trade_type', 'status']
possible_indirect_filters = ['location_ids']

def list_fcl_freight_rate_local_agents(filters = {}, page_limit = 10, page = 1, sort_by = 'updated_at', sort_type = 'desc', pagination_data_required = True):
    query = get_query(sort_by, sort_type, page, page_limit)

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)
        query = apply_direct_filters(query, filters, possible_direct_filters, FclFreightRateLocalAgent)
        query = apply_indirect_filters(query, filters)

    # with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    #     futures = [executor.submit(eval(method_name), query, page, page_limit, pagination_data_required) for method_name in ['get_data', 'get_pagination_data']]
    #     results = {}
    #     for future in futures:
    #         result = future.result()
    #         results.update(result)

    data = get_data(query)
    pagination_data = get_pagination_data(query, page, page_limit, pagination_data_required)

    return {'list': data } | (pagination_data)

def get_query(sort_by, sort_type, page, page_limit):
    query = FclFreightRateLocalAgent.select().order_by(eval('FclFreightRateLocalAgent.{}.{}()'.format(sort_by,sort_type))).paginate(page, page_limit)
    return query

def get_data(query):
    data = [model_to_dict(item) for item in query.execute()]

    return {'get_data':data}

# def add_service_objects(data):
#     service_objects = common.get_multiple_service_objects_data_for_fcl({'objects': [
#         {
#         'name': 'location',
#         'filters': { 'id': list(set([str(d['location_id']) for d in data if d.get('location_id')]))}, 

#         'fields': ['id', 'name', 'display_name', 'port_code', 'type']
#         },
#         {
#         'name': 'organization',
#         'filters': { 'id': list(set([str(d['service_provider_id']) for d in data if d.get('service_provider_id')])) },
#         'fields': ['id', 'business_name', 'short_name'],
#         'extra_params': { 'add_service_objects_required': False }
#         }
#     ]})
    
#     new_data = []
#     for objects in data:
#         objects['location'] = service_objects['location'][objects['location_id']] if 'location' in service_objects and objects.get('location_id') in service_objects['location'] else None
#         objects['service_provider'] = service_objects['organization'][objects['service_provider_id']] if 'organization' in service_objects and objects.get('service_provider_id') in service_objects['organization'] else None
#         new_data.append(objects)
    
#     return new_data

def get_pagination_data(data, page, page_limit, pagination_data_required):
    if not pagination_data_required:
        return {'get_pagination_data':{}} 

    params = {
      'page': page,
      'total': ceil(len(data)/page_limit),
      'total_count': len(data),
      'page_limit': page_limit
    }
    return {'get_pagination_data':params}

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query
 
def apply_location_ids_filter(query, filters):
    return query.where(FclFreightRateLocalAgent.location_ids.contains(filters['location_ids']))
