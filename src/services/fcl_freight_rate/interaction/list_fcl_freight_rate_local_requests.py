from services.fcl_freight_rate.models.fcl_freight_rate_local_request import FclFreightRateLocalRequest
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from services.fcl_freight_rate.helpers.find_or_initialize import apply_direct_filters
from playhouse.shortcuts import model_to_dict
from math import ceil
from datetime import datetime
import concurrent.futures, json
from peewee import fn, SQL
from micro_services.client import common

possible_indirect_filters = ['validity_start_greater_than', 'validity_end_less_than', 'similar_id']

possible_direct_filters = ['port_id','performed_by_id', 'status', 'closed_by_id', 'trade_id', 'country_id']


def list_fcl_freight_rate_local_requests(filters = {}, page_limit = 10, page = 1, is_stats_required = True, performed_by_id = None):
    query = FclFreightRateLocalRequest.select().order_by(FclFreightRateLocalRequest.created_at.desc())

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        query = apply_direct_filters(query, filters, possible_direct_filters, FclFreightRateLocalRequest)
        query = apply_indirect_filters(query, filters)

    query = query.paginate(page, page_limit)
    data = get_data(query)
    pagination_data = get_pagination_data(query, page, page_limit)

    stats = get_stats(query, filters, is_stats_required, performed_by_id) or {}

    return {'list': data } | (pagination_data) | (stats)

def apply_indirect_filters(query, filters):
  for key in filters:
    if key in possible_indirect_filters:
      apply_filter_function = f'apply_{key}_filter'
      query = eval(f'{apply_filter_function}(query, filters)')
  return query

def apply_validity_start_greater_than_filter(query, filters):
    return query.where(FclFreightRateLocalRequest.created_at >= datetime.strptime(filters['validity_start_greater_than'], '%Y-%m-%d'))

def apply_validity_end_less_than_filter(query, filters):
    return query.where(FclFreightRateLocalRequest.created_at <= datetime.strptime(filters['validity_end_less_than'], '%Y-%m-%d'))

def apply_similar_id_filter(query,filters):
    rate_request_obj = FclFreightRateLocalRequest.select(FclFreightRateLocalRequest.port_id, FclFreightRateLocalRequest.trade_type, FclFreightRateLocalRequest.container_size, FclFreightRateLocalRequest.container_type).where(FclFreightRateLocalRequest.id == filters['similar_id']).dicts().get()
    query = query.where(not(FclFreightRateLocalRequest.id == filters['similar_id']))
    return query.where(query.c.port_id == rate_request_obj['port_id'], query.c.trade_type == rate_request_obj['trade_type'], query.c.container_size == rate_request_obj['container_size'], query.c.container_type == rate_request_obj['container_type'])

def get_data(query):
    data = [model_to_dict(item) for item in query.execute()]
    return data

# def add_service_objects(data):
#     shipping_line_ids = list(set(filter(None, [item for sublist in [[d['preferred_shipping_line_ids'], d['shipping_line_id']] for d in data] for item in sublist])))
#     objects = [
#     {
#         'name': 'user',
#         'filters': { 'id': list(set([t['performed_by_id'] for t in data] + [t['closed_by_id'] for t in data]))},
#         'fields': ['id', 'name']
#     },
#     {
#         'name': 'location',
#         'filters': { 'id': list(set(item for sublist in [[item["port_id"]] for item in data] for item in sublist))},
#         'fields': ['id', 'name', 'display_name', 'port_code', 'type']
#     },
#     {
#         'name': 'operator',
#         'filters': { 'id': list(set(shipping_line_ids))},
#         'fields': ['id', 'business_name', 'short_name', 'logo_url']
#     },
#     {
#         'name': 'spot_search', 
#         'filters': {'id': list(set([t['source_id'] for t in data]))},
#         'fields': ['id', 'importer_exporter_id', 'importer_exporter', 'service_details']
#     }
#     ]

#     service_objects = common.get_multiple_service_objects_data_for_fcl({'objects': objects})
 
#     for i in range(len(data)):
#         data[i]['port'] = service_objects['location'][data[i]['port_id']] if 'location' in service_objects and data[i].get('port_id') in service_objects['location'] else None
#         data[i]['performed_by'] = service_objects['user'][data[i]['performed_by_id']] if 'user' in service_objects and data[i].get('performed_by_id') in service_objects['user'] else None
#         data[i]['closed_by'] = service_objects['user'][data[i]['closed_by_id']] if 'user' in service_objects and data[i].get('closed_by_id') in service_objects else None
#         data[i]['destination_port'] = service_objects['location'][data[i]['destination_port_id']]if 'location' in service_objects and data[i].get('destination_port_id') in service_objects else None
#         data[i]['cargo_readiness_date'] = data[i]['cargo_readiness_date'] if 'cargo_readiness_date' in data[i] else None
#         data[i]['closing_remarks'] = data[i]['closing_remarks'] if 'closing_remarks' in data[i] else None
#         data[i]['shipping_line_detail'] = service_objects['operator'][data[i]['shipping_line_id']] if 'operator' in service_objects and data[i].get('shipping_line_id') in service_objects['operator'] else None
#         data[i]['spot_search'] = service_objects['spot_search'][data[i]['source_id']] if 'spot_search' in service_objects and data[i].get('source_id') in service_objects['spot_search'] else None
    
#     return data


def get_pagination_data(query, page, page_limit):
  pagination_data = {
    'page': page,
    'total': ceil(query.count()/page_limit),
    'total_count': query.count(),
    'page_limit': page_limit
    }
  
  return pagination_data


def get_stats(query, filters, is_stats_required, performed_by_id):
    if not is_stats_required:
        return {} 

    query = FclFreightRateLocalRequest.select()
    
    if filters:
        if 'status' in filters:
            del filters['status']
    
        query = apply_direct_filters(query, filters, possible_direct_filters, FclFreightRateLocalRequest)
        query = apply_indirect_filters(query, filters)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(eval(method_name),query, performed_by_id) for method_name in ['get_total', 'get_total_closed_by_user', 'get_total_opened_by_user', 'get_status_count']]
        results = {}
        for future in futures:
            result = future.result()
            results.update(result)
    
    stats = {
        'total': results['get_total'],
        'total_closed_by_user': results['get_total_closed_by_user'],
        'total_opened_by_user': results['get_total_opened_by_user'],
        'total_open': results['get_status_count']['active'] if results['get_status_count'].get('active') else 0,
        'total_closed': results['get_status_count']['inactive'] if results['get_status_count'].get('inactive') else 0
    }
    return { 'stats': stats }

def get_total(query, performed_by_id):
    try:
        return {'get_total' : query.count()}
    except:
        return {'get_total' : {}}

def get_total_closed_by_user(query, performed_by_id):
    try:
        return {'get_total_closed_by_user' : query.where(FclFreightRateLocalRequest.status == 'inactive', FclFreightRateLocalRequest.closed_by_id == performed_by_id).count()}
    except:
        return {'get_total_closed_by_user' : {}}


def get_total_opened_by_user(query, performed_by_id):
    try:
        return {'get_total_opened_by_user' : query.where(FclFreightRateLocalRequest.status == 'active', FclFreightRateLocalRequest.closed_by_id == performed_by_id).count()}
    except:
        return {'get_total_opened_by_user' : {}}

def get_status_count(query, performed_by_id):
    try:
        query = query.select(FclFreightRateLocalRequest.status, fn.COUNT(SQL('*')).alias('count_all')).group_by(FclFreightRateLocalRequest.status)
        result = {}
        for row in query.execute():
            result[row.status] = row.count_all
        return {'get_status_count' : result}
    except:
        return {'get_status_count' : None}