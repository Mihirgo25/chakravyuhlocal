from services.fcl_customs_rate.models.fcl_customs_rate_request import FclCustomsRateRequest
import concurrent.futures, json
from libs.json_encoder import json_encoder
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
from micro_services.client import spot_search
from datetime import datetime
from database.rails_db import get_partner_user_experties, get_organization_service_experties
from math import ceil
from peewee import fn, SQL

possible_indirect_filters = ['relevant_supply_agent', 'validity_start_greater_than', 'validity_end_less_than', 'similar_id', 'supply_agent_id']

possible_direct_filters = ['port_id', 'performed_by_id', 'status', 'closed_by_id', 'country_id']

def list_fcl_customs_rate_requests(filters = {}, page_limit = 10, page = 1, performed_by_id = None, is_stats_required = True, spot_search_details_required=False):
    query = FclCustomsRateRequest.select()
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)
        
        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, FclCustomsRateRequest)
        query = apply_indirect_filters(query, indirect_filters)

    stats = get_stats(filters, is_stats_required, performed_by_id) or {}

    pagination_data = get_pagination_data(query, page, page_limit)
    query = get_page(query, page, page_limit)

    spot_search_hash = {}
    data = list(query.dicts())
    spot_search_ids = list(set([str(row['source_id']) for row in data]))
    try:
        spot_search_data = spot_search.list_spot_searches({'filters':{'id':spot_search_ids}})['list']
    except:
        spot_search_data = []

    for search in spot_search_data:
        spot_search_hash[search['id']] = {'id':search.get('id'), 'importer_exporter_id':search.get('importer_exporter_id'), 'importer_exporter':search.get('importer_exporter'), 'service_details':search.get('service_details')}

    for value in data:
        if str(value['source_id']) in spot_search_hash:
            value['spot_search'] = spot_search_hash[str(value['source_id'])]
        else:
            value['spot_search'] = {}

    return { 'list': json_encoder(data) } | (pagination_data) | (stats)

def get_page(query, page, page_limit):
    return query.select().order_by(FclCustomsRateRequest.created_at.desc()).paginate(page, page_limit)

def apply_indirect_filters(query, filters):
  for key in filters:
    if key in possible_indirect_filters:
      apply_filter_function = f'apply_{key}_filter'
      query = eval(f'{apply_filter_function}(query, filters)')
  return query

def apply_validity_start_greater_than_filter(query, filters):
    return query.where(FclCustomsRateRequest.created_at.cast('date') >= datetime.fromisoformat(filters['validity_start_greater_than']).date())

def apply_validity_end_less_than_filter(query, filters):
    return query.where(FclCustomsRateRequest.created_at.cast('date') <= datetime.fromisoformat(filters['validity_end_less_than']).date())

def apply_relevant_supply_agent_filter(query, filters):
    expertises = get_partner_user_experties('fcl_customs', filters['relevant_supply_agent'])
    location_id = [t['location_id'] for t in expertises]
    query = query.where((FclCustomsRateRequest.port_id << location_id) | (FclCustomsRateRequest.country_id << location_id))
    return query

def apply_supply_agent_id_filter(query, filters):
    expertises = get_organization_service_experties('fcl_customs', filters['supply_agent_id'])
    location_id = [t['location_id'] for t in expertises]
    query = query.where((FclCustomsRateRequest.port_id << location_id) | (FclCustomsRateRequest.country_id << location_id))
    return query

def apply_similar_id_filter(query,filters):
    rate_request_obj = FclCustomsRateRequest.select(FclCustomsRateRequest.port_id, FclCustomsRateRequest.trade_type, FclCustomsRateRequest.container_size, FclCustomsRateRequest.container_type, FclCustomsRateRequest.cargo_handling_type).where(FclCustomsRateRequest.id == filters['similar_id']).dicts().get()
    query = query.where(FclCustomsRateRequest.id != filters['similar_id'])
    return query.where(FclCustomsRateRequest.port_id == rate_request_obj['port_id'], FclCustomsRateRequest.trade_type == rate_request_obj['trade_type'], FclCustomsRateRequest.container_size == rate_request_obj['container_size'], FclCustomsRateRequest.container_type == rate_request_obj['container_type'], FclCustomsRateRequest.cargo_handling_type == rate_request_obj['cargo_handling_type'])

def get_pagination_data(query, page, page_limit):
    total_count = query.count()
    pagination_data = {
        'page': page,
        'total': ceil(total_count/page_limit),
        'total_count': total_count,
        'page_limit': page_limit
        }
    return pagination_data

def get_stats(filters, is_stats_required, performed_by_id):
    if not is_stats_required:
        return {} 

    query = FclCustomsRateRequest.select()

    if filters:
        if 'status' in filters:
            del filters['status']
        if 'closed_by_id' in filters:
            del filters['closed_by_id']
        
        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, FclCustomsRateRequest)
        query = apply_indirect_filters(query, indirect_filters)
    
    query = (
        query.select(
            fn.count(FclCustomsRateRequest.id).over().alias('get_total'),
            fn.count(FclCustomsRateRequest.id).filter(FclCustomsRateRequest.status == 'active').over().alias('get_status_count_active'),
            fn.count(FclCustomsRateRequest.id).filter(FclCustomsRateRequest.status == 'inactive').over().alias('get_status_count_inactive'),
            fn.count(FclCustomsRateRequest.id).filter((FclCustomsRateRequest.status=='inactive') & (FclCustomsRateRequest.closed_by_id==performed_by_id)).over().alias('get_total_closed_by_user'),
            fn.count(FclCustomsRateRequest.id).filter((FclCustomsRateRequest.status=='active')  & (FclCustomsRateRequest.performed_by_id==performed_by_id)).over().alias('get_total_opened_by_user'),
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

def get_total(query, performed_by_id):
    try:
        return {'get_total' : query.count()}
    except:
        return {'get_total' : None}
    
def get_total_closed_by_user(query, performed_by_id):
    try:
        return {'get_total_closed_by_user' : query.where(FclCustomsRateRequest.status == 'inactive', FclCustomsRateRequest.closed_by_id == performed_by_id).count() }
    except:
        return {'get_total_closed_by_user' : None}


def get_total_opened_by_user(query, performed_by_id):
    try:
        return {'get_total_opened_by_user' : query.where(FclCustomsRateRequest.status == 'active', FclCustomsRateRequest.closed_by_id == performed_by_id).count() }
    except:
        return {'get_total_opened_by_user' : None}

def get_status_count(query, performed_by_id):
    try:
        query = query.select(FclCustomsRateRequest.status, fn.COUNT(SQL('*')).alias('count_all')).group_by(FclCustomsRateRequest.status)
        result = {}
        for row in query.execute():
            result[row.status] = row.count_all
        return {'get_status_count' : result}
    except:
        return {'get_status_count' : None}