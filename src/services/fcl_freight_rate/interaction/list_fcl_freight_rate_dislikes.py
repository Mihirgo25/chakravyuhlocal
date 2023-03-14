from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from services.fcl_freight_rate.interaction.list_fcl_freight_rates import remove_unexpected_filters
from rails_client import client
from playhouse.shortcuts import model_to_dict
from math import ceil
from peewee import fn, JOIN
from operator import attrgetter
from datetime import datetime

possible_direct_filters = ['feedback_type', 'continent', 'status']

possible_indirect_filters = ['relevant_supply_agent', 'trade_lane', 'shipping_line', 'validity_start_greater_than', 'validity_end_less_than', 'service_provider_id']

def list_fcl_freight_rate_dislikes(filters, page, page_limit):
    filters = remove_unexpected_filters(filters)
    query = get_query(page, page_limit)
    query = apply_direct_filters(query, filters)
    query = apply_indirect_filters(query, filters)

    data = get_data(query)

    pagination_data = get_pagination_data(query)

    return { 'list': data } | (pagination_data)
    
def get_data(query):
    data = [model_to_dict(item) for item in query.execute()]
    data = add_service_objects(data)
    return data 

def add_service_objects(data):
    if data.count == 0:
        return [] 

    service_objects = client.ruby.get_multiple_service_object_data_for_fcl({'objects': [
    {
        'name': 'operator',
        'filters': { 'id': list(set([t['shipping_line_id'] for t in data]))},
        'fields': ['id', 'business_name', 'short_name', 'logo_url']
    },
    {
        'name': 'location',
        'filters': {"id": list(set(item for sublist in [[item["origin_trade_id"], item["destination_trade_id"]] for item in data] for item in sublist))},
        'fields': ['id', 'name', 'display_name']
    }
    ]})

    for i in range(len(data)):
        feedbacks_str = ','.join(data[i]['feedbacks']).translate(str.maketrans('', '', '{}"'))
        data[i]['feedbacks'] = feedbacks_str.split(',')
        data[i]['unpreferred_shipping_lines'] = len([t for t in list(set(data[i]['feedbacks'])) if t == 'unpreferred_shipping_lines'])
        data[i]['unsatisfactory_destination_detention'] = len([t for t in list(set(data[i]['feedbacks'])) if t == 'unsatisfactory_destination_detention'])
        data[i]['unsatisfactory_rate'] = len([t for t in list(set(data[i]['feedbacks'])) if t == 'unsatisfactory_rate'])
        data[i]['shipping_line'] = service_objects['operator'][data[i]['shipping_line_id']] if 'operator' in service_objects and data[i].get('shipping_line_id') in service_objects['operator'] else None
        data[i]['origin_trade'] = service_objects['location'][data[i]['origin_trade_id']] if 'location' in service_objects and data[i].get('origin_trade_id') in service_objects['location'] else None
        data[i]['destination_trade'] = service_objects['location'][data[i]['destination_trade_id']] if 'location' in service_objects and data[i].get('destination_trade_id') in service_objects['location'] else None
    
    return data

def get_query(page, page_limit):
    query = FclFreightRateFeedback.select().join(FclFreightRate, JOIN.INNER, on = (FclFreightRate.id == FclFreightRateFeedback.fcl_freight_rate_id)).where(FclFreightRateFeedback.feedback_type == 'disliked').paginate(page,page_limit)
    return query
    
def apply_direct_filters(query,filters):
  for key in filters:
    if key in possible_direct_filters:
      query = query.select().where(attrgetter(key)(FclFreightRateFeedback) == filters[key])
  return query

def apply_indirect_filters(query, filters):
  for key in filters:
    if key in possible_indirect_filters:
      apply_filter_function = f'apply_{key}_filter'
      query = eval(f'{apply_filter_function}(query, filters)')
  return query

def apply_trade_lane_filter(query, filters):
    return query.select(fn.array_agg(fn.filter_(fn.cast('feedbacks', 'text'), (fn.cast('feedbacks', 'text').not_in('{}')))).alias('feedbacks'), fn.COUNT(fn.concat_ws(' || ', query.c.origin_port_id, query.c.destination_port_id)).alias('port_pair_count').distinct(),query.c.origin_trade_id, query.c.destination_trade_id).group_by(query.c.origin_trade_id, query.c.destination_trade_id)

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
    expertises = client.ruby.list_partner_user_expertises({'filters': {'service_type': 'fcl_freight', 'partner_user_id': filters['relevant_supply_agent']}, 'page_limit': page_limit})['list']
    origin_port_id = [t['origin_location_id'] for t in expertises]
    destination_port_id =  [t['destination_location_id'] for t in expertises]
    query = query.where(FclFreightRate.origin_port_id == origin_port_id) or (query.where(FclFreightRate.origin_country_id == origin_port_id)) or (query.where(FclFreightRate.origin_continent_id == origin_port_id)) or (query.where(FclFreightRate.origin_trade_id == origin_port_id))
    query = query.where(FclFreightRate.destination_port_id == destination_port_id) or (query.where(FclFreightRate.destination_country_id == destination_port_id)) or (query.where(FclFreightRate.destination_continent_id == destination_port_id)) or (query.where(FclFreightRate.destination_trade_id == destination_port_id))
    return query

def get_pagination_data(query, page, page_limit):
  pagination_data = {
    'page': page,
    'total': ceil(query.count()/page_limit),
    'total_count': query.count(),
    'page_limit': page_limit
    }
  
  return pagination_data