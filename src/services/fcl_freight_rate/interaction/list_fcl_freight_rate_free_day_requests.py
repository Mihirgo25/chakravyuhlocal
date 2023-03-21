from services.fcl_freight_rate.models.fcl_freight_rate_free_day_request import FclFreightRateFreeDayRequest
from services.fcl_freight_rate.helpers.find_or_initialize import apply_direct_filters
from playhouse.shortcuts import model_to_dict
from math import ceil
import concurrent.futures, json
from rails_client import client
from datetime import datetime
from peewee import fn, SQL

possible_direct_filters = ['location_id', 'performed_by_id', 'status', 'closed_by_id', 'trade_type', 'free_day_type', 'country_id', 'container_size', 'container_type', 'service_provider_id']

possible_indirect_filters = ['validity_start_greater_than', 'validity_end_less_than']
 
def list_fcl_freight_rate_free_day_requests(filters = {}, page_limit = 10, page = 1, is_stats_required = True, performed_by_id = None):
    query = get_query(page, page_limit)

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        query = apply_direct_filters(query, filters, possible_direct_filters, FclFreightRateFreeDayRequest)
        query = apply_indirect_filters(query, filters)

    data = get_data(query)
    stats = get_stats(query, filters, is_stats_required, performed_by_id) or {}

    pagination_data = get_pagination_data(query, page, page_limit)

    return { 'list': data } | (pagination_data) | (stats)

def get_query(page, page_limit):
    return FclFreightRateFreeDayRequest.select().order_by(FclFreightRateFreeDayRequest.created_at.desc()).paginate(page, page_limit)

def apply_indirect_filters(query, filters):
  for key in filters:
    if key in possible_indirect_filters:
      apply_filter_function = f'apply_{key}_filter'
      query = eval(f'{apply_filter_function}(query, filters)')
  return query

def apply_validity_start_greater_than_filter(query, filters):
    return query.where(FclFreightRateFreeDayRequest.created_at >= datetime.strptime(filters['validity_start_greater_than'], '%Y-%m-%d'))

def apply_validity_end_less_than_filter(query, filters):
    return query.where(FclFreightRateFreeDayRequest.created_at <= datetime.strptime(filters['validity_end_less_than'], '%Y-%m-%d'))

def get_data(query):
    data = [model_to_dict(item) for item in query.execute()]
    return data

# def add_service_objects(data, spot_search_details_required):
#     shipping_line_ids = list(filter(None,[t['shipping_line_id'] for t in data]))
#     objects = [
#     {
#         'name': 'user',
#         'filters': { 'id': list(set([t['performed_by_id'] for t in data] + [t['closed_by_id'] for t in data]))},
#         'fields': ['id', 'name', 'email']
#     },
#     {
#         'name': 'location',
#         'filters': { 'id': list(set([t['location_id'] for t in data]))},
#         'fields': ['id', 'name', 'display_name', 'port_code', 'type']
#     },
#     {
#         'name': 'operator',
#         'filters': { 'id': list(set(shipping_line_ids)) },
#         'fields': ['id', 'business_name', 'short_name', 'logo_url']
#     },
#     {
#         'name': 'organization',
#         'filters': { 'id': list(set([t['service_provider_id'] for t in data]))},
#         'fields': ['id', 'business_name', 'short_name', 'logo']
#     }
#     ]
#     if spot_search_details_required:
#         objects.append({
#             'name': 'spot_search',
#             'filters': { 'id': list(set([t['source_id'] for t in data])) },
#             'fields': ['id', 'importer_exporter_id', 'importer_exporter', 'service_details']
#         })
    

#     service_objects = client.ruby.get_multiple_service_objects_data_for_fcl({'objects': objects})
    
#     for i in range(len(data)): 
#         data[i]['location']= service_objects['location'][data[i]['location_id']] if 'location' in service_objects and data[i].get('location_id') in service_objects['location'] else None
#         data[i]['performed_by'] = service_objects['user'][data[i]['performed_by_id']] if 'user' in service_objects and data[i].get('performed_by_id') in service_objects['user'] else None
#         data[i]['closed_by'] = service_objects['user'][data[i]['closed_by_id']] if 'user' in service_objects and data[i].get('closed_by_id') in service_objects['user'] else None
#         data[i]['shipping_line'] = service_objects['operator'][data[i]['shipping_line_id']] if 'operator' in service_objects and data[i].get('shipping_line_id') in service_objects['operator'] else None
#         data[i]['service_provider'] = service_objects['organization'][objects['service_provider_id']] if 'organization' in service_objects and data[i].get('service_provider_id') in service_objects['organization'] else None
#         data[i]['spot_search'] = service_objects['spot_search'][objects['source_id']] if 'spot_search' in service_objects and data[i].get('source_id') in service_objects['spot_search'] else None
    
#     return data

def get_pagination_data(query, page, page_limit):
    params = {
      'page': page,
      'total': ceil(query.count()/page_limit),
      'total_count': query.count(),
      'page_limit': page_limit
    }
    return params
  

def get_stats(query, filters, is_stats_required, performed_by_id):
    if not is_stats_required:
        return {}
    
    query = FclFreightRateFreeDayRequest.select()

    if filters:
        if 'status' in filters:
            del filters['status']
    
        query = apply_direct_filters(query, filters, possible_direct_filters, FclFreightRateFreeDayRequest)
        query = apply_indirect_filters(query, filters)

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(eval(method_name), query, performed_by_id) for method_name in ['get_total_closed_by_user', 'get_total_opened_by_user', 'get_status_count']]
        results = {}
        for future in futures:
            result = future.result()
            results.update(result)
    
    if results['get_status_count']:
        total_open = results['get_status_count'].get('active',0)
        total_closed = results['get_status_count'].get('inactive',0)
    else:
        total_open = 0
        total_closed = 0

    stats = {
        'total': total_open + total_closed,
        'total_closed_by_user': results['get_total_closed_by_user'],
        'total_opened_by_user': results['get_total_opened_by_user'],
        'total_open': total_open,
        'total_closed': total_closed
    }
    return { 'stats': stats }

def get_total_closed_by_user(query, performed_by_id):
    return {'get_total_closed_by_user' : query.where(FclFreightRateFreeDayRequest.status == 'inactive', FclFreightRateFreeDayRequest.closed_by_id == performed_by_id).count()}

def get_total_opened_by_user(query, performed_by_id):
    return {'get_total_opened_by_user' : query.where(FclFreightRateFreeDayRequest.status == 'active', FclFreightRateFreeDayRequest.performed_by_id == performed_by_id).count()}

def get_status_count(query, performed_by_id):
    query = query.select(FclFreightRateFreeDayRequest.status, fn.COUNT(SQL('*')).alias('count_all')).group_by(FclFreightRateFreeDayRequest.status)
    result = {}
    for row in query.execute():
        result[row.status] = row.count_all
    return {'get_status_count' : result}