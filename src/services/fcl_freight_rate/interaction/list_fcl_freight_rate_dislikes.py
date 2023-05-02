from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
from math import ceil
from peewee import fn
from datetime import datetime
import json
from micro_services.client import *
from database.rails_db import get_partner_user_experties

possible_direct_filters = ['feedback_type', 'continent', 'status']

possible_indirect_filters = ['relevant_supply_agent', 'trade_lane', 'shipping_line', 'validity_start_greater_than', 'validity_end_less_than', 'service_provider_id']

def list_fcl_freight_rate_dislikes(filters = {}, page_limit = 10, page = 1):
    query = get_query()

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)
        
        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, FclFreightRateFeedback)
        query = apply_indirect_filters(query, indirect_filters)

    pagination_data = get_pagination_data(query, page, page_limit)
    query = query.paginate(page,page_limit)

    data = get_data(query)
    return { 'list': data } | (pagination_data)
    
def get_data(query):
    data = []
    result = list(query.dicts())
    locations=[]
    for item in result:
        locations.append(str(item.get('origin_trade_id') or ''))
        item['origin_trade']=None
        locations.append(str(item.get('destination_trade_id') or ''))
        item['destination_trade']=None
        feedbacks_str = ','.join(item['feedbacks']).translate(str.maketrans('', '', '{}"'))
        item['feedbacks'] = feedbacks_str.split(',')
        unsatisfactory_rate_count = 0
        unpreferred_shipping_lines_count = 0
        unsatisfactory_destination_detention_count = 0

        for feedback in list(set(item['feedbacks'])):
            if feedback == 'unpreferred_shipping_lines':
                unpreferred_shipping_lines_count += 1
            if feedback == 'unsatisfactory_destination_detention':
                unsatisfactory_destination_detention_count+=1
            if feedback == 'unsatisfactory_rate':
                unsatisfactory_rate_count += 1
        
        item['unpreferred_shipping_lines'] = unpreferred_shipping_lines_count
        item['unsatisfactory_destination_detention'] = unsatisfactory_destination_detention_count
        item['unsatisfactory_rate'] = unsatisfactory_rate_count
        data.append(item)
    locations_data = maps.list_locations({'filters':{'id':locations},'page_limit': 100})['list']
    location_match = {}
    for location in locations_data:
        location_match[location['id']] = {key:value for key,value in location.items() if key in ['id', 'name', 'display_name']}
    
    for i in range(0,len(data)):
        if data[i].get('origin_trade_id'):
            data[i]['origin_trade'] = location_match[str(data[i]['origin_trade_id'])]
        if data[i].get('destination_trade_id'):
             data[i]['destination_trade'] = location_match[str(data[i]['destination_trade_id'])]
           
    return data 

def get_query():
    query = FclFreightRateFeedback.select(FclFreightRateFeedback, FclFreightRate.origin_trade_id, FclFreightRate.destination_trade_id, FclFreightRate.shipping_line).join(FclFreightRate, on = (FclFreightRateFeedback.fcl_freight_rate_id == FclFreightRate.id)
    ).where(FclFreightRateFeedback.feedback_type == 'disliked')
    return query

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query


def apply_trade_lane_filter(query, filters):
    return query.select(
        fn.array_agg((
            fn.CONCAT(FclFreightRate.origin_port_id, '||', FclFreightRate.destination_port_id)
            ).distinct()
        ).alias('feedbacks'),
        fn.count((fn.CONCAT(FclFreightRate.origin_port_id, ' || ', FclFreightRate.destination_port_id)).distinct()).alias('port_pair_count'),
        FclFreightRate.origin_trade_id,
        FclFreightRate.destination_trade_id
    ).where(FclFreightRateFeedback.feedbacks.cast('VARCHAR') != '{}').group_by(
        FclFreightRate.origin_trade_id,
        FclFreightRate.destination_trade_id
    )
    
def apply_service_provider_id_filter(query, filters):
    query = query.where(FclFreightRate.service_provider_id == filters['service_provider_id'])
    return query

def apply_shipping_line_filter(query, filters):
    return query.select(
        fn.array_agg((
            fn.CONCAT(FclFreightRate.origin_port_id, '||', FclFreightRate.destination_port_id)
            ).distinct()
        ).alias('feedbacks'),
        fn.count((fn.CONCAT(FclFreightRate.origin_port_id, ' || ', FclFreightRate.destination_port_id)).distinct()).alias('port_pair_count'),
        FclFreightRate.shipping_line_id
    ).where(FclFreightRateFeedback.feedbacks.cast('VARCHAR') != '{}').group_by(
        FclFreightRate.shipping_line_id
    )
    
def apply_validity_start_greater_than_filter(query, filters):
    query = query.where(FclFreightRateFeedback.created_at.cast('date') >= datetime.fromisoformat(filters['validity_start_greater_than']).date())
    return query

def apply_validity_end_less_than_filter(query, filters):
    query = query.where(FclFreightRateFeedback.created_at.cast('date') <= datetime.fromisoformat(filters['validity_end_less_than']).date())
    return query

def apply_relevant_supply_agent_filter(query, filters):
    expertises = get_partner_user_experties('fcl_freight', filters['relevant_supply_agent'])
    origin_port_id = [t['origin_location_id'] for t in expertises]
    destination_port_id =  [t['destination_location_id'] for t in expertises]
    query = query.where((FclFreightRate.origin_port_id << origin_port_id) | (FclFreightRate.origin_country_id << origin_port_id) | (FclFreightRate.origin_continent_id << origin_port_id) | (FclFreightRate.origin_trade_id << origin_port_id))
    query = query.where((FclFreightRate.destination_port_id << destination_port_id) | (FclFreightRate.destination_country_id << destination_port_id) | (FclFreightRate.destination_continent_id << destination_port_id) | (FclFreightRate.destination_trade_id << destination_port_id))
    return query

def get_pagination_data(query, page, page_limit):
  total_count = query.count()
  
  pagination_data = {
    'page': page,
    'total': ceil(total_count/page_limit),
    'total_count': total_count,
    'page_limit': page_limit
    }
  
  return pagination_data