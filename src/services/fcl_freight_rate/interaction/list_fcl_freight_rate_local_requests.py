from services.fcl_freight_rate.models.fcl_freight_rate_local_request import FclFreightRateLocalRequest
from math import ceil
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
import concurrent.futures, json
from peewee import fn, SQL

possible_indirect_filters = ['validity_start_greater_than', 'validity_end_less_than', 'similar_id']

possible_direct_filters = ['port_id','performed_by_id', 'status', 'closed_by_id', 'trade_id', 'country_id']


def list_fcl_freight_rate_local_requests(filters = {}, page_limit = 10, page = 1, is_stats_required = True, performed_by_id = None):
    query = FclFreightRateLocalRequest.select().order_by(FclFreightRateLocalRequest.created_at.desc())

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)
        
        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, FclFreightRateLocalRequest)
        query = apply_indirect_filters(query, indirect_filters)

    query = query.paginate(page, page_limit)

    data = jsonable_encoder(list(query.dicts()))

    pagination_data = get_pagination_data(data, page, page_limit)

    stats = get_stats(filters, is_stats_required, performed_by_id) or {}

    return {'list': data } | (pagination_data) | (stats)

def apply_indirect_filters(query, filters):
  for key in filters:
    if key in possible_indirect_filters:
      apply_filter_function = f'apply_{key}_filter'
      query = eval(f'{apply_filter_function}(query, filters)')
  return query

def apply_validity_start_greater_than_filter(query, filters):
    return query.where(FclFreightRateLocalRequest.created_at.cast('date') >= datetime.strptime(filters['validity_start_greater_than'], '%Y-%m-%dT%H:%M:%S.%f%z').date())

def apply_validity_end_less_than_filter(query, filters):
    return query.where(FclFreightRateLocalRequest.created_at.cast('date') <= datetime.strptime(filters['validity_end_less_than'], '%Y-%m-%dT%H:%M:%S.%f%z').date())

def apply_similar_id_filter(query,filters):
    rate_request_obj = FclFreightRateLocalRequest.select(FclFreightRateLocalRequest.port_id, FclFreightRateLocalRequest.trade_type, FclFreightRateLocalRequest.container_size, FclFreightRateLocalRequest.container_type).where(FclFreightRateLocalRequest.id == filters['similar_id']).dicts().get()
    query = query.where(FclFreightRateLocalRequest.id != filters['similar_id'])
    return query.where(FclFreightRateLocalRequest.port_id == rate_request_obj['port_id'], FclFreightRateLocalRequest.trade_type == rate_request_obj['trade_type'], FclFreightRateLocalRequest.container_size == rate_request_obj['container_size'], FclFreightRateLocalRequest.container_type == rate_request_obj['container_type'])


def get_pagination_data(data, page, page_limit):
  pagination_data = {
    'page': page,
    'total': ceil(len(data)/page_limit),
    'total_count': len(data),
    'page_limit': page_limit
    }
  
  return pagination_data


def get_stats(filters, is_stats_required, performed_by_id):
    if not is_stats_required:
        return {} 

    query = FclFreightRateLocalRequest.select()
    
    if filters:
        if 'status' in filters:
            del filters['status']
    
        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, FclFreightRateLocalRequest)
        query = apply_indirect_filters(query, indirect_filters)

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