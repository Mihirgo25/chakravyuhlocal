from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from configs.fcl_freight_rate_constants import RATE_ENTITY_MAPPING
from playhouse.shortcuts import model_to_dict
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
from database.rails_db import get_partner_user_experties, get_organization_service_experties
from datetime import datetime
import concurrent.futures, json
from peewee import fn, SQL
from math import ceil

possible_direct_filters = ['feedback_type', 'performed_by_org_id', 'performed_by_id', 'closed_by_id', 'status']
possible_indirect_filters = ['relevant_supply_agent', 'supply_agent_id','origin_port_id', 'destination_port_id', 'validity_start_greater_than', 'validity_end_less_than', 'origin_trade_id', 'destination_trade_id', 'shipping_line_id', 'similar_id', 'origin_country_id', 'destination_country_id', 'service_provider_id', 'cogo_entity_id']

def list_fcl_freight_rate_feedbacks(filters = {}, page_limit =10, page=1, performed_by_id=None, is_stats_required=True):
    query = FclFreightRateFeedback.select()

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, FclFreightRateFeedback)
        query = apply_indirect_filters(query, indirect_filters)
        
    query = get_join_query(query)
    query = query.select(FclFreightRateFeedback, FclFreightRate.origin_port, FclFreightRate.destination_port, FclFreightRate.shipping_line)
    stats = get_stats(filters, is_stats_required, performed_by_id) or {}

    query = get_page(query, page, page_limit)
    data = get_data(query)

    pagination_data = get_pagination_data(data, page, page_limit)
    return {'list': data } | (pagination_data) | (stats)

def get_page(query, page, page_limit):
    query = query.order_by(FclFreightRateFeedback.created_at.desc(nulls='LAST')).paginate(page, page_limit)
    return query

def get_join_query(query):
    query = query.join(FclFreightRate, on=(FclFreightRateFeedback.fcl_freight_rate_id == FclFreightRate.id))
    return query

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query

def apply_relevant_supply_agent_filter(query, filters):
    expertises = get_partner_user_experties('fcl_freight', filters['relevant_supply_agent'])
    origin_port_id = [t['origin_location_id'] for t in expertises]
    destination_port_id = [t['destination_location_id'] for t in expertises]
    query = query.where((FclFreightRate.origin_port_id << origin_port_id) |
                    (FclFreightRate.origin_country_id << origin_port_id) |
                    (FclFreightRate.origin_continent_id << origin_port_id) |
                    (FclFreightRate.origin_trade_id << origin_port_id))
    query = query.where((FclFreightRate.destination_port_id << destination_port_id) |
                    (FclFreightRate.destination_country_id << destination_port_id) |
                    (FclFreightRate.destination_continent_id << destination_port_id) |
                    (FclFreightRate.destination_trade_id << destination_port_id))
    return query

def apply_supply_agent_id_filter(query, filters):
    expertises = get_organization_service_experties('fcl_freight', filters['supply_agent_id'])
    origin_port_id = [t['origin_location_id'] for t in expertises]
    destination_port_id = [t['destination_location_id'] for t in expertises]
    query = query.where((FclFreightRate.origin_port_id << origin_port_id) |
                    (FclFreightRate.origin_country_id << origin_port_id) |
                    (FclFreightRate.origin_continent_id << origin_port_id) |
                    (FclFreightRate.origin_trade_id << origin_port_id))
    query = query.where((FclFreightRate.destination_port_id << destination_port_id) |
                    (FclFreightRate.destination_country_id << destination_port_id) |
                    (FclFreightRate.destination_continent_id << destination_port_id) |
                    (FclFreightRate.destination_trade_id << destination_port_id))
    return query

def apply_cogo_entity_id_filter(query, filters):
    filter_entity_id = filters['cogo_entity_id']

    cogo_entity_ids = None
    if filter_entity_id in RATE_ENTITY_MAPPING:
        cogo_entity_ids = RATE_ENTITY_MAPPING[filter_entity_id]

    query = query.where(FclFreightRate.cogo_entity_id << cogo_entity_ids)

    return query

def apply_service_provider_id_filter(query, filters):
    query = query.where(FclFreightRate.service_provider_id == filters['service_provider_id'])
    return query

def apply_validity_start_greater_than_filter(query, filters):
    query = query.where(FclFreightRateFeedback.created_at.cast('date') >= datetime.strptime(filters['validity_start_greater_than'],'%Y-%m-%dT%H:%M:%S.%fz').date())

    return query

def apply_validity_end_less_than_filter(query, filters):
    query = query.where(FclFreightRate.created_at.cast('date') <= datetime.strptime(filters['validity_end_less_than'],'%Y-%m-%dT%H:%M:%S.%fz').date())

    return query

def apply_origin_port_id_filter(query, filters):
    query = query.where(FclFreightRate.origin_port_id == filters['origin_port_id'])
    return query

def apply_destination_port_id_filter(query, filters):
    query = query.where(FclFreightRate.destination_port_id == filters['destination_port_id'])
    return query

def apply_origin_country_id_filter(query, filters):
    query = query.where(FclFreightRate.origin_country_id == filters['origin_country_id'])
    return query

def apply_destination_country_id_filter(query, filters):
    query = query.where(FclFreightRate.destination_country_id == filters['destination_country_id'])
    return query

def apply_origin_trade_id_filter(query, filters):
    query = query.where(FclFreightRate.origin_trade_id == filters['origin_trade_id'])
    return query

def apply_destination_trade_id_filter(query, filters):
    query = query.where(FclFreightRate.destination_trade_id == filters['destination_trade_id'])
    return query

def apply_shipping_line_id_filter(query, filters):
    query = query.where(FclFreightRate.shipping_line_id == filters['shipping_line_id'])
    return query

def apply_similar_id_filter(query, filters):
    feedback_data = (FclFreightRateFeedback
         .select(FclFreightRate.origin_port_id, FclFreightRate.destination_port_id, FclFreightRate.container_size, FclFreightRate.container_type, FclFreightRate.commodity)
         .join(FclFreightRate, on=(FclFreightRateFeedback.fcl_freight_rate_id == FclFreightRate.id))
         .where(FclFreightRateFeedback.id == filters['similar_id'])
         .limit(1))

    query = query.where(FclFreightRateFeedback.id != filters.get('similar_id'))
    query = query.where(FclFreightRate.origin_port_id == feedback_data.origin_port_id, FclFreightRate.destination_port_id == feedback_data.destination_port_id, FclFreightRate.container_size == feedback_data.container_size, FclFreightRate.container_type == feedback_data.container_type, FclFreightRate.commodity == feedback_data.commodity)

    return query

def get_data(query):
    data = list(query.dicts())
    fcl_freight_rate_ids = [row['fcl_freight_rate_id'] for row in data]
    fcl_freight_rates = list(FclFreightRate.select().where(FclFreightRate.id.in_(fcl_freight_rate_ids)).dicts())
    fcl_freight_rate_mappings = {k['id']: k for k in fcl_freight_rates}

    new_data = []
    for object in data:
        rate = fcl_freight_rate_mappings[object.get('fcl_freight_rate_id', None)] or {}
        object['container_size'] = rate.get('container_size')
        object['container_type'] = rate.get('container_type')
        object['commodity'] = rate.get('commodity')
        object['containers_count'] = object['booking_params'].get('containers_count', None)
        object['bls_count'] = object['booking_params'].get('bls_count', None)
        object['inco_term'] = object['booking_params'].get('inco_term', None)
        try:
            price_currency = [t for t in rate['validities'] if t['id'] == object.get('validity_id')][0]
            object['price'] = price_currency['price']
            object['currency'] = price_currency['currency']
        except:
            object['price'] = None
            object['currency'] = None

        if object['booking_params'].get('rate_card', {}).get('service_rates', {}):
            for key, value in object['booking_params']['rate_card']['service_rates'].items():
                service_provider = object.get('service_provider_id', None)
                if service_provider:
                    object['booking_params']['rate_card']['service_rates'][key]['service_provider'] = service_provider
        new_data.append(object)
    return new_data

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
    
    query = FclFreightRateFeedback.select()

    if filters:
        if 'status' in filters:
            del filters['status']
        
        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, FclFreightRateFeedback)
        query = apply_indirect_filters(query, indirect_filters)

    query = get_join_query(query)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(eval(method_name), query, performed_by_id) for method_name in ['get_total', 'get_total_closed_by_user', 'get_total_opened_by_user', 'get_status_count']]
        method_responses = {}
        for future in futures:
            result = future.result()
            method_responses.update(result)  

    stats = {
      'total': method_responses['get_total'],
      'total_closed_by_user': method_responses['get_total_closed_by_user'],
      'total_opened_by_user': method_responses['get_total_opened_by_user'],
      'total_open': method_responses['get_status_count'].get('active') if method_responses['get_status_count'] else 0,
      'total_closed': method_responses['get_status_count'].get('inactive') if method_responses['get_status_count'] else 0
    }
    return { 'stats': stats }

def get_total(query, performed_by_id):
    try:
        return {'get_total':query.count()}
    except:
        return {'get_total' : 0}

def get_total_closed_by_user(query, performed_by_id):
    try:
        return {'get_total_closed_by_user':query.where(FclFreightRateFeedback.status == 'inactive', FclFreightRateFeedback.closed_by_id == performed_by_id).count() }
    except:
        return {'get_total_closed_by_user':0}


def get_total_opened_by_user(query, performed_by_id):
    try:
        return {'get_total_opened_by_user' : query.where(FclFreightRateFeedback.status == 'active', FclFreightRateFeedback.closed_by_id == performed_by_id).count() }
    except:
        return {'get_total_opened_by_user' : 0}

def get_status_count(query, performed_by_id):
    try:
        query = query.select(FclFreightRateFeedback.status, fn.COUNT(SQL('*')).alias('count_all')).group_by(FclFreightRateFeedback.status)
        result = {}
        for row in query.execute():
            result[row.status] = row.count_all
        return {'get_status_count' : result}
    except:
        return {'get_status_count' : 0}