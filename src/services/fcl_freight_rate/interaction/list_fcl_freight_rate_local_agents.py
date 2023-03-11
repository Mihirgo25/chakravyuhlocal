from rails_client import client
import concurrent.futures
from services.fcl_freight_rate.models.fcl_freight_rate_local_agent import FclFreightRateLocalAgent
from playhouse.shortcuts import model_to_dict
from operator import attrgetter
import uuid
from math import ceil
from peewee import fn
import json

possible_direct_filters = ['service_provider_id', 'trade_type', 'status']
possible_indirect_filters = ['location_ids']

def list_fcl_freight_rate_local_agents(filters = {}, page_limit = 10, page = 1, sort_by = 'updated_at', sort_type = 'desc', pagination_data_required = True, add_service_objects_required = True):
    if type(filters) != dict:
        filters = json.loads(filters)

    query = get_query(sort_by, sort_type, page, page_limit)
    query = apply_direct_filters(query, filters)
    query = apply_indirect_filters(query, filters)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(eval(method_name), query, page, page_limit, pagination_data_required, add_service_objects_required) for method_name in ['get_data', 'get_pagination_data']]
        results = {}
        for future in futures:
            result = future.result()
            results.update(result)

    data = results['get_data']
    pagination_data = results['get_pagination_data']

    return {'list': data } | (pagination_data)

def get_query(sort_by, sort_type, page, page_limit):
    query = FclFreightRateLocalAgent.select().order_by(eval('FclFreightRateLocalAgent.{}.{}()'.format(sort_by,sort_type))).paginate(page, page_limit)
    return query

def get_data(query, page, page_limit, pagination_data_required, add_service_objects_required):
    data = [model_to_dict(item) for item in query.execute()]
    if not add_service_objects_required:
        return {'get_data':data} 

    data = add_service_objects(data)
    return {'get_data':data}

def add_service_objects(data):
    service_objects = client.ruby.get_multiple_service_objects_data_for_fcl({'objects': [
        {
        'name': 'location',
        'filters': { 'id': list(set([str(d['location_id']) for d in data if d.get('location_id')]))}, 

        'fields': ['id', 'name', 'display_name', 'port_code', 'type']
        },
        {
        'name': 'organization',
        'filters': { 'id': list(set([str(d['service_provider_id']) for d in data if d.get('service_provider_id')])) },
        'fields': ['id', 'business_name', 'short_name'],
        'extra_params': { 'add_service_objects_required': False }
        }
    ]})
    
    new_data = []
    for objects in data:
        objects['location'] = service_objects['location'][objects['location_id']] if 'location' in service_objects and objects.get('location_id') in service_objects['location'] else None
        objects['service_provider'] = service_objects['organization'][objects['service_provider_id']] if 'organization' in service_objects and objects.get('service_provider_id') in service_objects['organization'] else None
        new_data.append(objects)
    
    return new_data

def get_pagination_data(query, page, page_limit, pagination_data_required, add_service_objects_required):
    if not pagination_data_required:
        return {'get_pagination_data':{}} 

    params = {
      'page': page,
      'total': ceil(query.count()/page_limit),
      'total_count': query.count(),
      'page_limit': page_limit
    }
    return {'get_pagination_data':params}

def apply_direct_filters(query, filters):
    for key in filters:
        if key in possible_direct_filters:
            query = query.select().where(attrgetter(key)(FclFreightRateLocalAgent) == filters[key])
    return query

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query
 
def apply_location_ids_filter(query, filters):
    location_ids = [uuid.UUID(id.strip()) for id in filters['location_ids'][1:-1].split(',')]
    return query.where(FclFreightRateLocalAgent.location_ids.contains(location_ids))
