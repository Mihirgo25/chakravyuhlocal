from services.fcl_freight_rate.models.fcl_freight_rate_free_day import FclFreightRateFreeDay
from services.fcl_freight_rate.interaction.list_fcl_freight_rates import remove_unexpected_filters
from operator import attrgetter
from math import ceil
from rails_client import client
import concurrent.futures

possible_direct_filters = ['id', 'port_id', 'country_id', 'trade_id', 'continent_id', 'shipping_line_id', 'service_provider_id', 'importer_exporter_id', 'trade_type', 'free_days_type', 'container_size', 'container_type', 'is_slabs_missing', 'location_id', 'specificity_type', 'previous_days_applicable', 'rate_not_available_entry']
possible_indirect_filters = ['importer_exporter_present']

def list_fcl_freight_rate_free_days(filters, page_limit, page, pagination_data_required, return_query):
    filters = remove_unexpected_filters(filters)
    query = get_query(page, page_limit)
    query = apply_direct_filters(query, filters)
    query = apply_indirect_filters(query, filters)
    
    if return_query:
        return { 'list': query } 
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(eval(method_name), query, page, page_limit, pagination_data_required) for method_name in ['get_data', 'get_pagination_data']]
        results = {}
        for future in futures:
            result = future.result()
            results.update(result)
        
    method_responses = results
    data = method_responses['get_data']
    pagination_data = method_responses['get_pagination_data']

    return {'list': data} | (pagination_data)

def get_query(page, page_limit):
    query = FclFreightRateFreeDay.order_by(FclFreightRateFreeDay.updated_at.desc()).paginate(page, page_limit)
    return query

def get_data(query, page, page_limit, pagination_data_required):
    data = query.select(
        FclFreightRateFreeDay.id,
        FclFreightRateFreeDay.location_id,
        FclFreightRateFreeDay.shipping_line_id,
        FclFreightRateFreeDay.service_provider_id,
        FclFreightRateFreeDay.importer_exporter_id,
        FclFreightRateFreeDay.trade_type,
        FclFreightRateFreeDay.free_days_type,
        FclFreightRateFreeDay.container_size,
        FclFreightRateFreeDay.container_type,
        FclFreightRateFreeDay.free_limit,
        FclFreightRateFreeDay.remarks,
        FclFreightRateFreeDay.slabs,
        FclFreightRateFreeDay.is_slabs_missing,
        FclFreightRateFreeDay.specificity_type,
        FclFreightRateFreeDay.updated_at,
        FclFreightRateFreeDay.previous_days_applicable
    ).dicts()

    data = add_service_objects(data)
    return data

def add_service_objects(data):
    service_objects = client.ruby.get_multiple_service_objects_for_fcl({'objects': [
        {
        'name': 'operator',
        'filters': { 'id': list(set(str(item["shipping_line_id"]) for item in data))},
        'fields': ['id', 'business_name', 'short_name', 'logo_url']
        },
        {
        'name': 'location',
        'filters': { 'id': list(set(item for sublist in [str(item["location_id"]) for item in data] for item in sublist)) },
        'fields': ['id', 'name', 'display_name', 'port_code', 'type']
        },
        {
        'name': 'organization',
        'filters': { 'id': list(set(item for sublist in [[str(item["service_provider_id"]), str(item["importer_exporter_id"])] for item in data] for item in sublist))},
        'fields': ['id', 'business_name', 'short_name']
        }
    ]})
    
    new_data = []
    for objects in data:
        objects['shipping_line'] = service_objects['operator'][objects['shipping_line_id']] if 'operator' in service_objects and objects.get('shipping_line_id') in service_objects['operator'] else None
        objects['location'] = service_objects['location'][objects['location_id']] if 'location' in service_objects and objects.get('location_id') in service_objects['location'] else None
        objects['service_provider'] = service_objects['organization'][objects['service_provider_id']] if 'organization' in service_objects and objects.get('service_provider_id') in service_objects['organization'] else None
        objects['importer_exporter'] = service_objects['organization'][objects['importer_exporter_id']] if 'organization' in service_objects and objects.get('importer_exporter_id') in service_objects['organization'] else None
        new_data.append(objects)
        return new_data

def get_pagination_data(query, page, page_limit, pagination_data_required):
    if pagination_data_required:
        return {} 

    params = {
      'page': page,
      'total': ceil(query.count()/page_limit),
      'total_count': query.count(),
      'page_limit': page_limit
    }
    return params

def apply_direct_filters(query, filters):
    for key in filters:
        if key in possible_direct_filters:
            query = query.select().where(attrgetter(key)(FclFreightRateFreeDay) == filters[key])
    return query

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query

def apply_importer_exporter_present_filter(query, filters):
    if filters['importer_exporter_present'] == True:
        return query.where(not(FclFreightRateFreeDay.importer_exporter_id == None)) 

    query = query.where(FclFreightRateFreeDay.importer_exporter_id == None)
    return query

