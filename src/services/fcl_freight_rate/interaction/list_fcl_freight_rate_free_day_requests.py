from services.fcl_freight_rate.models.fcl_freight_rate_free_day_request import FclFreightRateFreeDayRequest
from services.fcl_freight_rate.helpers.find_or_initialize import apply_direct_filters
from playhouse.shortcuts import model_to_dict
from math import ceil
import concurrent.futures, json
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
    stats = get_stats(filters, is_stats_required, performed_by_id) or {}

    pagination_data = get_pagination_data(data, page, page_limit)

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

def get_pagination_data(data, page, page_limit):
    params = {
      'page': page,
      'total': ceil(len(data)/page_limit),
      'total_count': len(data),
      'page_limit': page_limit
    }
    return params
  

def get_stats(filters, is_stats_required, performed_by_id):
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