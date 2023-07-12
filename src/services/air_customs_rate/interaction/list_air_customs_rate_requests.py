from services.air_customs_rate.models.air_customs_rate_request import AirCustomsRateRequest
import json
from libs.json_encoder import json_encoder
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
from datetime import datetime
from database.rails_db import get_partner_user_experties
from math import ceil
from peewee import fn

possible_indirect_filters = ['relevant_supply_agent', 'validity_start_greater_than', 'validity_end_less_than', 'similar_id']

possible_direct_filters = ['airport_id', 'performed_by_id', 'status', 'closed_by_id', 'country_id','trade_id']

def list_air_customs_rate_requests(filters = {}, page_limit = 10, page = 1, performed_by_id = None, is_stats_required = True, spot_search_details_required=False):
    query = AirCustomsRateRequest.select()
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)
        
        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)

        query = get_filters(direct_filters, query, AirCustomsRateRequest)
        query = apply_indirect_filters(query, indirect_filters)

    stats = get_stats(filters, is_stats_required, performed_by_id) or {}

    pagination_data = get_pagination_data(query, page, page_limit)
    query = get_page(query, page, page_limit)

    data = list(query.dicts())

    return { 'list': json_encoder(data) } | (pagination_data) | (stats)

def get_page(query, page, page_limit):
    return query.select().order_by(AirCustomsRateRequest.created_at.desc()).paginate(page, page_limit)

def apply_indirect_filters(query, filters):
  for key in filters:
    if key in possible_indirect_filters:
      apply_filter_function = f'apply_{key}_filter'
      query = eval(f'{apply_filter_function}(query, filters)')
  return query

def apply_validity_start_greater_than_filter(query, filters):
    return query.where(AirCustomsRateRequest.created_at.cast('date') >= datetime.fromisoformat(filters['validity_start_greater_than'].split('T')[0]).date())

def apply_validity_end_less_than_filter(query, filters):
    return query.where(AirCustomsRateRequest.created_at.cast('date') <= datetime.fromisoformat(filters['validity_end_less_than'].split('T')[0]).date())

def apply_relevant_supply_agent_filter(query, filters):
    expertises = get_partner_user_experties('air_customs', filters['relevant_supply_agent'])
    location_id = [t['location_id'] for t in expertises]
    query = query.where((AirCustomsRateRequest.airport_id << location_id) | (AirCustomsRateRequest.country_id << location_id) |(AirCustomsRateRequest.continent_id << location_id) |(AirCustomsRateRequest.city_id << location_id))
    return query

def apply_similar_id_filter(query,filters):
    rate_request_obj = AirCustomsRateRequest.select(AirCustomsRateRequest.airport_id, AirCustomsRateRequest.trade_type, AirCustomsRateRequest.weight, AirCustomsRateRequest.volume, AirCustomsRateRequest.commodity).where(AirCustomsRateRequest.id == filters['similar_id']).dicts().get()
    query = query.where(AirCustomsRateRequest.id != filters['similar_id'])
    return query.where(AirCustomsRateRequest.airport_id == rate_request_obj['airport_id'], AirCustomsRateRequest.trade_type == rate_request_obj['trade_type'], AirCustomsRateRequest.weight == rate_request_obj['weight'], AirCustomsRateRequest.volume == rate_request_obj['volume'], AirCustomsRateRequest.commodity == rate_request_obj['commodity'])

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

    query = AirCustomsRateRequest.select()

    if filters:
        if 'status' in filters:
            del filters['status']

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)

        query = get_filters(direct_filters, query, AirCustomsRateRequest)
        query = apply_indirect_filters(query, indirect_filters)

    query = (
        query.select(
            fn.count(AirCustomsRateRequest.id).over().alias('get_total'),
            fn.count(AirCustomsRateRequest.id).filter(AirCustomsRateRequest.status == 'active').over().alias('get_status_count_active'),
            fn.count(AirCustomsRateRequest.id).filter(AirCustomsRateRequest.status == 'inactive').over().alias('get_status_count_inactive'),
            fn.count(AirCustomsRateRequest.id).filter((AirCustomsRateRequest.status=='inactive') & (AirCustomsRateRequest.closed_by_id==performed_by_id)).over().alias('get_total_closed_by_user'),
            fn.count(AirCustomsRateRequest.id).filter((AirCustomsRateRequest.status=='active')  & (AirCustomsRateRequest.performed_by_id==performed_by_id)).over().alias('get_total_opened_by_user'),
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