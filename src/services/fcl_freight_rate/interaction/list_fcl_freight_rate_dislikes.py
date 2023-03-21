from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from services.fcl_freight_rate.helpers.find_or_initialize import apply_direct_filters
from math import ceil
from peewee import fn, JOIN
from datetime import datetime
import json
from micro_services.client import *

possible_direct_filters = ['feedback_type', 'continent', 'status']

possible_indirect_filters = ['relevant_supply_agent', 'trade_lane', 'shipping_line', 'validity_start_greater_than', 'validity_end_less_than', 'service_provider_id']

def list_fcl_freight_rate_dislikes(filters = {}, page_limit = 10, page = 1):
    query = get_query(page, page_limit)
    
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        query = apply_direct_filters(query, filters, possible_direct_filters, FclFreightRateFeedback)
        query = apply_indirect_filters(query, filters)
    print(query)
    data = get_data(query)
    
    pagination_data = get_pagination_data(query, page, page_limit)
    
    return { 'list': data } | (pagination_data)
    
def get_data(query):
    data = []
    for item in query.dicts():
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
    return data 

def get_query(page, page_limit):
    query = FclFreightRateFeedback.select().join(FclFreightRate, JOIN.INNER, on = (FclFreightRate.id == FclFreightRateFeedback.fcl_freight_rate_id)).where(FclFreightRateFeedback.feedback_type == 'disliked').paginate(page,page_limit)
    return query

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query

# def apply_trade_lane_filter(query, filters):
#     return query.select(fn.array_agg(fn.filter_(fn.cast('feedbacks', 'text'), (fn.cast('feedbacks', 'text').not_in('{}')))).alias('feedbacks'), fn.COUNT(fn.concat_ws(' || ', query.c.origin_port_id, query.c.destination_port_id)).alias('port_pair_count').distinct(),query.c.origin_trade_id, query.c.destination_trade_id).group_by(query.c.origin_trade_id, query.c.destination_trade_id)

def apply_trade_lane_filter(query, filters):
    return query.select(
        fn.array_agg((fn.concat_ws(' || ', FclFreightRate.origin_port_id, FclFreightRate.destination_port_id))).alias('feedbacks').distinct(),
        fn.count((fn.concat_ws(' || ', FclFreightRate.origin_port_id, FclFreightRate.destination_port_id))).alias('port_pair_count').distinct(),
        FclFreightRate.origin_trade_id,
        FclFreightRate.destination_trade_id
    ).where(FclFreightRateFeedback.feedbacks != '{}').group_by(
        FclFreightRate.origin_trade_id,
        FclFreightRate.destination_trade_id
    )
    

def apply_service_provider_id_filter(query, filters):
    query = query.where(FclFreightRate.service_provider_id == filters['service_provider_id'])
    return query

def apply_shipping_line_filter(query, filters):
    return query.select(fn.array_agg(fn.filter_(fn.cast('feedbacks', 'text'), (fn.cast('feedbacks', 'text').not_in('{}')))).alias('feedbacks'), fn.COUNT(fn.concat_ws(' || ', query.c.origin_port_id, query.c.destination_port_id)).alias('port_pair_count').distinct(), query.c.shipping_line_id).group_by(query.c.shipping_line_id)
    
def apply_validity_start_greater_than_filter(query, filters):
    query = query.where(FclFreightRateFeedback.created_at >= datetime.strptime(filters['validity_start_greater_than'], '%Y-%m-%d'))
    return query

def apply_validity_end_less_than_filter(query, filters):
    query = query.where(FclFreightRateFeedback.created_at <= datetime.strptime(filters['validity_end_less_than'], '%Y-%m-%d'))
    return query

def apply_relevant_supply_agent_filter(query, filters):
    page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
    expertises = partner.list_partner_user_expertises({'filters': {'service_type': 'fcl_freight', 'partner_user_id': filters['relevant_supply_agent']}, 'page_limit': page_limit})['list']
    origin_port_id = [t['origin_location_id'] for t in expertises]
    destination_port_id =  [t['destination_location_id'] for t in expertises]
    query = query.where((FclFreightRate.origin_port_id << origin_port_id) | (FclFreightRate.origin_country_id << origin_port_id) | (FclFreightRate.origin_continent_id << origin_port_id) | (FclFreightRate.origin_trade_id << origin_port_id))
    query = query.where((FclFreightRate.destination_port_id << destination_port_id) | (FclFreightRate.destination_country_id << destination_port_id) | (FclFreightRate.destination_continent_id << destination_port_id) | (FclFreightRate.destination_trade_id << destination_port_id))
    return query

def get_pagination_data(query, page, page_limit):
  pagination_data = {
    'page': page,
    'total': ceil(query.count()/page_limit),
    'total_count': query.count(),
    'page_limit': page_limit
    }
  
  return pagination_data