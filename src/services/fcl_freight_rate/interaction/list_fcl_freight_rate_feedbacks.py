from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from configs.fcl_freight_rate_constants import RATE_CONSTANT_MAPPING
from playhouse.shortcuts import model_to_dict
from rails_client import client
from datetime import datetime
import json
from operator import attrgetter
import concurrent.futures
from peewee import fn
from math import ceil


possible_direct_filters = ['feedback_type', 'performed_by_org_id', 'performed_by_id', 'closed_by_id', 'status']
possible_indirect_filters = ['relevant_supply_agent', 'origin_port_id', 'destination_port_id', 'validity_start_greater_than', 'validity_end_less_than', 'origin_trade_id', 'destination_trade_id', 'shipping_line_id', 'similar_id', 'origin_country_id', 'destination_country_id', 'service_provider_id', 'cogo_entity_id']

def remove_unexpected_filters(filters):
    filters = json.loads(filters)
    expected_filters = set(possible_direct_filters + possible_indirect_filters).intersection(set(filters.keys()))
    expected_filters = {key:filters[key] for key in list(expected_filters) if key in expected_filters}

    return expected_filters

def list_fcl_freight_rate_feedbacks(filters, page_limit, page, is_stats_required, performed_by_id, spot_search_details_required):
    filters = remove_unexpected_filters(filters)

    query = FclFreightRateFeedback.select()
    query = apply_direct_filters(query, filters)
    query = apply_indirect_filters(query, filters)
    query = get_join_query(query)
    stats = get_stats(query) or {}
    query = get_page(query)
    data = get_data(query)

def get_page(query, page, page_limit):
    query = query.order_by(FclFreightRateFeedback.created_at.desc()).paginate(page, page_limit)
    return query

def get_join_query(query):
    query = query.join(FclFreightRate, on=(FclFreightRateFeedback.fcl_freight_rate_id == FclFreightRate.id))
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

def apply_relevant_supply_agent_filter(query, filters):
    page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
    expertises = client.ruby.list_partner_user_expertises({ 'filters': { 'service_type': 'fcl_freight', 'partner_user_id': filters['relevant_supply_agent'] }, page_limit: page_limit })['list']
    origin_port_id = [t['origin_location_id'] for t in expertises]
    destination_port_id = [t['destination_location_id'] for t in expertises]
    query = query.where((FclFreightRate.origin_port_id == origin_port_id) |
                    (FclFreightRate.origin_country_id == origin_port_id) |
                    (FclFreightRate.origin_continent_id == origin_port_id) |
                    (FclFreightRate.origin_trade_id == origin_port_id))
    query = query.where((FclFreightRate.destination_port_id == destination_port_id) |
                    (FclFreightRate.destination_country_id == destination_port_id) |
                    (FclFreightRate.destination_continent_id == destination_port_id) |
                    (FclFreightRate.destination_trade_id == destination_port_id))
    return query

def apply_cogo_entity_id_filter(query, filters):
    filter_entity_id = filters['cogo_entity_id']

    cogo_entity_ids = [t["cogo_entity_id"] for t in RATE_CONSTANT_MAPPING if filter_entity_id in t["allowed_entity_ids"] if t["cogo_entity_id"]]
    query = query.where(FclFreightRate.cogo_entity_id == cogo_entity_ids)

    return query

def apply_service_provider_id_filter(query, filters):
    query = query.where(FclFreightRate.service_provider_id == filters['service_provider_id'])
    return query

def apply_validity_start_greater_than_filter(query, filters):
    query = query.where(FclFreightRateFeedback.created_at >= datetime.strptime(filters['validity_start_greater_than'],'%Y-%m-%d'))
    return query

def apply_validity_end_less_than_filter(query, filters):
    query = query.where(FclFreightRate.created_at <= datetime.strptime(filters['validity_end_less_than'],'%Y-%m-%d'))
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
         .first())

    query = query.where(~(FclFreightRateFeedback.id == filters.get('similar_id')))
    query = query.where(FclFreightRate.origin_port_id == feedback_data.origin_port_id, FclFreightRate.destination_port_id == feedback_data.destination_port_id, FclFreightRate.container_size == feedback_data.container_size, FclFreightRate.container_type == feedback_data.container_type, FclFreightRate.commodity == feedback_data.commodity)

    return query


def get_data(query):
    data = [model_to_dict(row, recurse=False) for row in query]
    add_service_objects(data)

def add_service_objects(data, spot_search_details_required):
    fcl_freight_rate_ids = [row['fcl_freight_rate_id'] for row in data]
    fcl_freight_rates = (FclFreightRate.select().where(FclFreightRate.id.in_(fcl_freight_rate_ids)))
    fcl_freight_rates = [model_to_dict(rate) for rate in fcl_freight_rates]
    fcl_freight_rate_mappings = {k['id']: k for k in fcl_freight_rates}
    shipping_line_ids = [i for obj in data for i in obj.get('preferred_shipping_line_ids', [])] + [rate.get('shipping_line_id') for rate in fcl_freight_rates]
    service_provider_id_hash = {}
    organisation_ids = []
    for obj in data:
        if obj.get('booking_params') and obj['booking_params'].get('rate_card') and obj['booking_params']['rate_card'].get('service_rates'):
            for key, value in obj['booking_params']['rate_card']['service_rates'].items():
                service_provider_id_hash[key] = value['service_provider_id']
                organisation_ids.append(value['service_provider_id'])

    organisation_ids = list(set([obj['performed_by_org_id'] for obj in data]))

    objects = [    
        { 
            'name': 'user',
            'filters': {'id': list(set(data[i]['performed_by_id'] for i in range(len(data))) | set(data[i]['closed_by_id'] for i in range(len(data))))},
            'fields': ['id', 'name', 'email', 'mobile_country_code', 'mobile_number']
        },
        {
            'name': 'location',
            'filters': {'id': list(set([fcl_freight_rates[i]['origin_port_id'] for i in range(len(fcl_freight_rates))]) | set([fcl_freight_rates[i]['destination_port_id'] for i in range(len(fcl_freight_rates))]))},
            'fields': ['id', 'name', 'display_name', 'port_code', 'type']
        },
        {
            'name': 'operator',
            'filters': {'id': shipping_line_ids},
            'fields': ['id', 'business_name', 'short_name', 'logo_url']
        },
        {
            'name': 'organization',
            'filters': {'id': list(set(organisation_ids))},
            'fields': ['id', 'business_name', 'short_name'],
            'extra_params': {'add_service_objects_required': False}
        }
    ]
    if spot_search_details_required:
        objects.append({
            'name': 'spot_search',
            'filters': {'id': list(set([d.get('source_id') for d in data]))},
            'fields': ['id', 'importer_exporter_id', 'importer_exporter', 'service_details']
        })

    service_objects = client.ruby.get_multiple_service_objects_data_for_fcl({"objects": objects})
    for object in data:
        rate = fcl_freight_rate_mappings[object.get('fcl_freight_rate_id', None)] or {}
        object['performed_by'] = service_objects['user'].get(object.get('performed_by_id'), None)
        object['closed_by'] = service_objects['user'].get(object.get('closed_by_id'), None)
        object['origin_port'] = service_objects['location'].get(rate.get('origin_port_id'), None)
        object['destination_port'] = service_objects['location'].get(rate.get('destination_port_id'), None)
        object['preferred_detention_free_days'] = object.get('preferred_detention_free_days')
        object['closing_remarks'] = object.get('closing_remarks')
        object['container_size'] = rate.get('container_size')
        object['container_type'] = rate.get('container_type')
        object['commodity'] = rate.get('commodity')
        object['shipping_line'] = service_objects['operator'].get(rate.get('shipping_line_id'), None)
        object['organization'] = service_objects['organization'].get(object.get('performed_by_org_id'), None)
        object['containers_count'] = object['booking_params'].get('containers_count', None)
        object['bls_count'] = object['booking_params'].get('bls_count', None)
        object['inco_term'] = object['booking_params'].get('inco_term', None)
        object['price'] = next((t['price'] for t in rate['validities'] if t['id'] == object.get('validity_id')), None)
        object['currency'] = next((t['currency'] for t in rate['validities'] if t['id'] == object.get('validity_id')), None)
        object['preferred_shipping_lines'] = []
        for id in object.get('preferred_shipping_line_ids', []):
            shipping_line = service_objects['operator'].get(id, None)
        if shipping_line:
            object['preferred_shipping_lines'].append(shipping_line)
            object['spot_search'] = service_objects['spot_search'].get(object.get('source_id'), None)
        if object['booking_params'].get('rate_card', {}).get('service_rates', {}):
            for key, value in object['booking_params']['rate_card']['service_rates'].items():
                service_provider = service_objects['organization'].get(value.get('service_provider_id'), None)
        if service_provider:
            object['booking_params']['rate_card']['service_rates'][key]['service_provider'] = service_provider

def get_pagination_data(query, page, page_limit):
    params = {
      'page': page,
      'total': ceil(query.count()/page_limit),
      'total_count': query.count(),
      'page_limit': page_limit
    }
    return params

def get_stats(query, is_stats_required, performed_by_id):
    if not is_stats_required:
        return {}

    query = query.unwhere(FclFreightRateFeedback.status)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(eval(method_name), query, performed_by_id) for method_name in ['get_total', 'get_total_closed_by_user', 'get_total_opened_by_user', 'get_status_count']]
        results = {}
        for future in futures:
            result = future.result()
            results.update(result)  #we don't need this update last line me hi ho jaa rha (once check)

    method_responses = result
    stats = {
      'total': method_responses['get_total'],
      'total_closed_by_user': method_responses['get_total_closed_by_user'],
      'total_opened_by_user': method_responses['get_total_opened_by_user'],
      'total_open': method_responses['get_status_count']['active'] if method_responses['get_status_count'] else 0,
      'total_closed': method_responses['get_status_count']['inactive'] if method_responses['get_status_count'] else 0
    }
    return { 'stats': stats }

def get_total(query):
    try:
        count = query.count()
    except:
        count = None
    return count

def get_total_closed_by_user(query, performed_by_id):
    count = query.where(FclFreightRateFeedback.status == 'inactive', FclFreightRateFeedback.closed_by_id == performed_by_id).count() or None
    return count

def get_total_opened_by_user(query, performed_by_id):
    count = query.where(FclFreightRateFeedback.status =='active', FclFreightRateFeedback.closed_by_id == performed_by_id).count() or None
    return count

def get_status_count(query):
    count = query.group_by(FclFreightRateFeedback.status).select(FclFreightRateFeedback.status, fn.COUNT(FclFreightRateFeedback.id)).execute() or None
    return count
