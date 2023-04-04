from services.fcl_freight_rate.models.fcl_freight_rate_free_day_request import FclFreightRateFreeDayRequest
from playhouse.shortcuts import model_to_dict
from math import ceil
from fastapi.encoders import jsonable_encoder
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
import concurrent.futures, json
from datetime import datetime
from peewee import fn, SQL
from micro_services.client import spot_search
possible_direct_filters = ['location_id', 'performed_by_id', 'status', 'closed_by_id', 'trade_type', 'free_day_type', 'country_id', 'container_size', 'container_type', 'service_provider_id']

possible_indirect_filters = ['validity_start_greater_than', 'validity_end_less_than']
 
def list_fcl_freight_rate_free_day_requests(filters = {}, page_limit = 10, page = 1, is_stats_required = True, performed_by_id = None):
    query = FclFreightRateFreeDayRequest.select().order_by(FclFreightRateFreeDayRequest.created_at.desc())

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, FclFreightRateFreeDayRequest)
        query = apply_indirect_filters(query, indirect_filters)

    pagination_data = get_pagination_data(query, page, page_limit)
    query = query.paginate(page, page_limit)

    spot_search_hash = {}
    data = list(query.dicts())
    spot_search_ids = list(set([str(row['source_id']) for row in data]))
    spot_search_data = spot_search.list_spot_searches({'filters':{'id':spot_search_ids}})['list']
    for search in spot_search_data:
        spot_search_hash[search['id']] = {'id':search.get('id'), 'importer_exporter_id':search.get('importer_exporter_id'), 'importer_exporter':search.get('importer_exporter'), 'service_details':search.get('service_details')}

    for index in range(0,len(data)):
        data[index]['spot_search'] = spot_search_hash[str(data[index]['source_id'])]


    stats = get_stats(filters, is_stats_required, performed_by_id) or {}

    return { 'list': jsonable_encoder(data) } | (pagination_data) | (stats)

def apply_indirect_filters(query, filters):
  for key in filters:
    if key in possible_indirect_filters:
      apply_filter_function = f'apply_{key}_filter'
      query = eval(f'{apply_filter_function}(query, filters)')
  return query

def apply_validity_start_greater_than_filter(query, filters):
    return query.where(FclFreightRateFreeDayRequest.created_at.cast('date') >= datetime.strptime(filters['validity_start_greater_than'], '%Y-%m-%d').date())

def apply_validity_end_less_than_filter(query, filters):
    return query.where(FclFreightRateFreeDayRequest.created_at.cast('date') <= datetime.strptime(filters['validity_end_less_than'], '%Y-%m-%d').date())

def get_data(query):
    data = [model_to_dict(item) for item in query.execute()]
    return data

def get_pagination_data(query, page, page_limit):
    total_count = query.count()
    params = {
      'page': page,
      'total': ceil(total_count/page_limit),
      'total_count': total_count,
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
    
        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, FclFreightRateFreeDayRequest)
        query = apply_indirect_filters(query, indirect_filters)

    # with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    #     futures = [executor.submit(eval(method_name), query, performed_by_id) for method_name in ['get_total_closed_by_user', 'get_total_opened_by_user', 'get_status_count']]
    #     results = {}
    #     for future in futures:
    #         result = future.result()
    #         results.update(result)
    
    # if results['get_status_count']:
    #     total_open = results['get_status_count'].get('active',0)
    #     total_closed = results['get_status_count'].get('inactive',0)
    # else:
    #     total_open = 0
    #     total_closed = 0

    # stats = {
    #     'total': total_open + total_closed,
    #     'total_closed_by_user': results['get_total_closed_by_user'],
    #     'total_opened_by_user': results['get_total_opened_by_user'],
    #     'total_open': total_open,
    #     'total_closed': total_closed
    # }

        query = (query.select(
        fn.count(FclFreightRateFreeDayRequest.id).over().alias('get_total'),
        fn.count(FclFreightRateFreeDayRequest.id).filter(FclFreightRateFreeDayRequest.status == 'active').over().alias('get_status_count_active'),
        fn.count(FclFreightRateFreeDayRequest.id).filter(FclFreightRateFreeDayRequest.status == 'inactive').over().alias('get_status_count_inactive'),
        fn.count(FclFreightRateFreeDayRequest.id).filter((FclFreightRateFreeDayRequest.status=='inactive') & (FclFreightRateFreeDayRequest.closed_by_id==performed_by_id)).over().alias('get_total_closed_by_user'),
        fn.count(FclFreightRateFreeDayRequest.id).filter((FclFreightRateFreeDayRequest.status=='active')  & (FclFreightRateFreeDayRequest.performed_by_id==performed_by_id)).over().alias('get_total_opened_by_user'),

         )
    ).limit(1)

    result = query.execute()
    if len(result)>0:
        result =result[0]
        stats = {
        'total': result.get_total,
        'total_closed_by_user': result.get_total_closed_by_user,
        'total_opened_by_user': result.get_total_opened_by_user,
        'total_open': result.get_status_count_active,
        'total_closed': result.get_status_count_inactive
        }
    else:
        stats ={}
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