from services.fcl_freight_rate.models.fcl_freight_rate_request import FclFreightRateRequest
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from micro_services.client import *
from math import ceil
from peewee import fn, SQL
import concurrent.futures, json
from fastapi.encoders import jsonable_encoder
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
from database.rails_db import get_partner_user_experties, get_organization_service_experties
from datetime import datetime
possible_direct_filters = ['origin_port_id', 'destination_port_id', 'performed_by_id', 'status', 'closed_by_id', 'origin_trade_id', 'destination_trade_id', 'origin_country_id', 'destination_country_id', 'cogo_entity_id']

possible_indirect_filters = ['relevant_supply_agent', 'validity_start_greater_than', 'validity_end_less_than', 'similar_id', 'supply_agent_id']

def list_fcl_freight_rate_requests(filters = {}, page_limit = 10, page = 1, performed_by_id = None, is_stats_required = True):
    query = FclFreightRateRequest.select()
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)
        
        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, FclFreightRateRequest)
        query = apply_indirect_filters(query, indirect_filters)

    stats = get_stats(filters, is_stats_required, performed_by_id) or {}
    query = get_page(query, page, page_limit)
    data = jsonable_encoder(list(query.dicts()))

    pagination_data = get_pagination_data(data, page, page_limit)

    return { 'list': data } | (pagination_data) | (stats)

def get_page(query, page, page_limit):
    return query.select().order_by(FclFreightRateRequest.created_at.desc()).paginate(page, page_limit)

def apply_indirect_filters(query, filters):
  for key in filters:
    if key in possible_indirect_filters:
      apply_filter_function = f'apply_{key}_filter'
      query = eval(f'{apply_filter_function}(query, filters)')
  return query

def apply_validity_start_greater_than_filter(query, filters):
    return query.where(FclFreightRateRequest.created_at.cast('date') >= datetime.strptime(filters['validity_start_greater_than'],'%Y-%m-%dT%H:%M:%S.%fz').date())

def apply_validity_end_less_than_filter(query, filters):
    return query.where(FclFreightRateRequest.created_at.cast('date') <= datetime.strptime(filters['validity_end_less_than'],'%Y-%m-%dT%H:%M:%S.%fz').date())

def apply_relevant_supply_agent_filter(query, filters):
    expertises = get_partner_user_experties('fcl_freight', filters['relevant_supply_agent'])
    origin_port_id = [t['origin_location_id'] for t in expertises]
    destination_port_id =  [t['destination_location_id'] for t in expertises]
    query = query.where((FclFreightRateRequest.origin_port_id << origin_port_id)) | (FclFreightRateRequest.origin_country_id << origin_port_id) | (FclFreightRateRequest.origin_continent_id << origin_port_id) | (FclFreightRateRequest.origin_trade_id << origin_port_id)
    query = query.where((FclFreightRateRequest.destination_port_id << destination_port_id) | (FclFreightRateRequest.destination_country_id << destination_port_id) | (FclFreightRateRequest.destination_continent_id << destination_port_id) | (FclFreightRateRequest.destination_trade_id << destination_port_id))
    return query

def apply_supply_agent_id_filter(query, filters):
    expertises = get_organization_service_experties('fcl_freight', filters['supply_agent_id'])
    origin_port_id = [t['origin_location_id'] for t in expertises]
    destination_port_id =  [t['destination_location_id'] for t in expertises]
    query = query.where((FclFreightRateRequest.origin_port_id << origin_port_id)) | (FclFreightRateRequest.origin_country_id << origin_port_id) | (FclFreightRateRequest.origin_continent_id << origin_port_id) | (FclFreightRateRequest.origin_trade_id << origin_port_id)
    query = query.where((FclFreightRateRequest.destination_port_id << destination_port_id) | (FclFreightRateRequest.destination_country_id << destination_port_id) | (FclFreightRateRequest.destination_continent_id << destination_port_id) | (FclFreightRateRequest.destination_trade_id << destination_port_id))
    return query

def apply_similar_id_filter(query,filters):
    rate_request_obj = FclFreightRateRequest.select().where(FclFreightRateRequest.id == filters['similar_id']).dicts().get()
    query = query.where(FclFreightRateRequest.id != filters['similar_id'])
    return query.where(FclFreightRateRequest.origin_port_id == rate_request_obj['origin_port_id'], FclFreightRateRequest.destination_port_id == rate_request_obj['destination_port_id'], FclFreightRateRequest.container_size == rate_request_obj['container_size'], FclFreightRateRequest.container_type == rate_request_obj['container_type'], FclFreightRateRequest.commodity == rate_request_obj['commodity'], FclFreightRateRequest.inco_term == rate_request_obj['inco_term'])


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

    query = FclFreightRateRequest.select()

    if filters:
        if 'status' in filters:
            del filters['status']
        
        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, FclFreightRateRequest)
        query = apply_indirect_filters(query, indirect_filters)
    
    query = (
        query
        .select(
            fn.count(FclFreightRateRequest.id).over().alias('get_total'),
          fn.count(FclFreightRateRequest.id).filter(FclFreightRateRequest.status == 'active').over().alias('get_status_count_active'),
        fn.count(FclFreightRateRequest.id).filter(FclFreightRateRequest.status == 'inactive').over().alias('get_status_count_inactive'),
        fn.count(FclFreightRateRequest.id).filter((FclFreightRateRequest.status=='inactive') & (FclFreightRateRequest.closed_by_id==performed_by_id)).over().alias('get_total_closed_by_user'),
        fn.count(FclFreightRateRequest.id).filter((FclFreightRateRequest.status=='active')  & (FclFreightRateRequest.performed_by_id==performed_by_id)).over().alias('get_total_opened_by_user'),

         )
    ).limit(1)
    result = query.dicts().get()

    # with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    #     futures = [executor.submit(eval(method_name), query, performed_by_id) for method_name in ['get_total', 'get_total_closed_by_user', 'get_total_opened_by_user', 'get_status_count']]
    #     results = {}
    #     for future in futures:
    #         result = future.result()
    #         results.update(result)

    stats = {
      'total': result['get_total'],
      'total_closed_by_user': result['get_total_closed_by_user'],
      'total_opened_by_user': result['get_total_opened_by_user'],
      'total_open': result['get_status_count_active'],
      'total_closed': result['get_status_count_inactive']
    }
    return { 'stats': stats }


# def get_total(query, performed_by_id):
#     try:
#         return {'get_total':query.count()}
#     except:
#         return {'get_total' : None}

# def get_total_closed_by_user(query, performed_by_id):
#     try:
#         return {'get_total_closed_by_user':query.where(FclFreightRateRequest.status == 'inactive', FclFreightRateRequest.closed_by_id == performed_by_id).count() }
#     except:
#         return {'get_total_closed_by_user':None}


# def get_total_opened_by_user(query, performed_by_id):
#     try:
#         return {'get_total_opened_by_user' : query.where(FclFreightRateRequest.status == 'active', FclFreightRateRequest.closed_by_id == performed_by_id).count() }
#     except:
#         return {'get_total_opened_by_user' : None}

# def get_status_count(query, performed_by_id):
#     try:
#         query = query.select(FclFreightRateRequest.status, fn.COUNT(SQL('*')).alias('count_all')).group_by(FclFreightRateRequest.status)
#         result = {}
#         for row in query.execute():
#             result[row.status] = row.count_all
#         return {'get_status_count' : result}
#     except:
#         return {'get_status_count' : None}