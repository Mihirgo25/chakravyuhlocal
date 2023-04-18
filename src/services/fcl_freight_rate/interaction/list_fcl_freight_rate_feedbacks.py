from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from configs.fcl_freight_rate_constants import RATE_ENTITY_MAPPING
from playhouse.shortcuts import model_to_dict
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
from database.rails_db import get_partner_user_experties, get_organization_service_experties
from datetime import datetime
import concurrent.futures, json
from peewee import fn, SQL,Window
from math import ceil
from micro_services.client import spot_search
from database.rails_db import get_organization
possible_direct_filters = ['feedback_type', 'performed_by_org_id', 'performed_by_id', 'closed_by_id', 'status']
possible_indirect_filters = ['relevant_supply_agent', 'supply_agent_id','origin_port_id', 'destination_port_id', 'validity_start_greater_than', 'validity_end_less_than', 'origin_trade_id', 'destination_trade_id', 'similar_id', 'origin_country_id', 'destination_country_id', 'service_provider_id', 'cogo_entity_id', 'relevant_service_provider_id']

def list_fcl_freight_rate_feedbacks(filters = {},spot_search_details_required=False, page_limit =10, page=1, performed_by_id=None, is_stats_required=True, booking_details_required=False):
    query = FclFreightRateFeedback.select()

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)

        query = get_filters(direct_filters, query, FclFreightRateFeedback)
        query = apply_indirect_filters(query, indirect_filters)

    # query = get_join_query(query)
    query = query.select()
    stats = get_stats(filters, is_stats_required, performed_by_id) or {}
    pagination_data = get_pagination_data(query, page, page_limit)

    query = get_page(query, page, page_limit)
    data = get_data(query,spot_search_details_required,booking_details_required) 

    return {'list': data } | (pagination_data) | (stats)

def get_page(query, page, page_limit):
    query = query.order_by(FclFreightRateFeedback.created_at.desc(nulls='LAST')).paginate(page, page_limit)
    return query

# def get_join_query(query):
#     query = query.join(FclFreightRate, on=( FclFreightRateFeedback.fcl_freight_rate_id == FclFreightRate.id))
#     return query

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
    query = query.where((FclFreightRateFeedback.origin_port_id << origin_port_id) |
                    (FclFreightRateFeedback.origin_country_id << origin_port_id) |
                    (FclFreightRateFeedback.origin_continent_id << origin_port_id) |
                    (FclFreightRateFeedback.origin_trade_id << origin_port_id))
    query = query.where((FclFreightRateFeedback.destination_port_id << destination_port_id) |
                    (FclFreightRateFeedback.destination_country_id << destination_port_id) |
                    (FclFreightRateFeedback.destination_continent_id << destination_port_id) |
                    (FclFreightRateFeedback.destination_trade_id << destination_port_id))
    return query

def apply_relevant_service_provider_id_filter(query, filters):
    expertises = get_organization_service_experties('fcl_freight', filters['relevant_service_provider_id'], account_type='organization')
    origin_port_id = [t['origin_location_id'] for t in expertises]
    destination_port_id =  [t['destination_location_id'] for t in expertises]
    query = query.where((FclFreightRateFeedback.origin_port_id << origin_port_id) | (FclFreightRateFeedback.origin_country_id << origin_port_id) | (FclFreightRateFeedback.origin_continent_id << origin_port_id) | (FclFreightRateFeedback.origin_trade_id << origin_port_id))
    query = query.where((FclFreightRateFeedback.destination_port_id << destination_port_id) | (FclFreightRateFeedback.destination_country_id << destination_port_id) | (FclFreightRateFeedback.destination_continent_id << destination_port_id) | (FclFreightRateFeedback.destination_trade_id << destination_port_id))
    return query

def apply_supply_agent_id_filter(query, filters):
    expertises = get_organization_service_experties('fcl_freight', filters['supply_agent_id'])
    origin_port_id = [t['origin_location_id'] for t in expertises]
    destination_port_id = [t['destination_location_id'] for t in expertises]
    query = query.where((FclFreightRateFeedback.origin_port_id << origin_port_id) |
                    (FclFreightRateFeedback.origin_country_id << origin_port_id) |
                    (FclFreightRateFeedback.origin_continent_id << origin_port_id) |
                    (FclFreightRateFeedback.origin_trade_id << origin_port_id))
    query = query.where((FclFreightRateFeedback.destination_port_id << destination_port_id) |
                    (FclFreightRateFeedback.destination_country_id << destination_port_id) |
                    (FclFreightRateFeedback.destination_continent_id << destination_port_id) |
                    (FclFreightRateFeedback.destination_trade_id << destination_port_id))
    return query

def apply_cogo_entity_id_filter(query, filters):
    filter_entity_id = filters['cogo_entity_id']

    query = query.where((FclFreightRateFeedback.cogo_entity_id == filter_entity_id) | (FclFreightRateFeedback.cogo_entity_id.is_null(True)))
    return query

def apply_service_provider_id_filter(query, filters):
    query = query.where(FclFreightRateFeedback.service_provider_id == filters['service_provider_id'])
    return query

def apply_validity_start_greater_than_filter(query, filters):
    query = query.where(FclFreightRateFeedback.created_at.cast('date') >= datetime.fromisoformat(filters['validity_start_greater_than']).date())

    return query

def apply_validity_end_less_than_filter(query, filters):
    query = query.where(FclFreightRateFeedback.created_at.cast('date') <= datetime.fromisoformat(filters['validity_end_less_than']).date())

    return query

def apply_origin_port_id_filter(query, filters):
    query = query.where(FclFreightRateFeedback.origin_port_id == filters['origin_port_id'])
    return query

def apply_destination_port_id_filter(query, filters):
    query = query.where(FclFreightRateFeedback.destination_port_id == filters['destination_port_id'])
    return query

def apply_origin_country_id_filter(query, filters):
    query = query.where(FclFreightRateFeedback.origin_country_id == filters['origin_country_id'])
    return query

def apply_destination_country_id_filter(query, filters):
    query = query.where(FclFreightRateFeedback.destination_country_id == filters['destination_country_id'])
    return query

def apply_origin_trade_id_filter(query, filters):
    query = query.where(FclFreightRateFeedback.origin_trade_id == filters['origin_trade_id'])
    return query

def apply_destination_trade_id_filter(query, filters):
    query = query.where(FclFreightRateFeedback.destination_trade_id == filters['destination_trade_id'])
    return query

def apply_shipping_line_id_filter(query, filters):
    query = query.where(FclFreightRateFeedback.shipping_line_id == filters['shipping_line_id'])
    return query

def apply_similar_id_filter(query, filters):
    feedback_data = (FclFreightRateFeedback.select(FclFreightRateFeedback.origin_port_id, FclFreightRateFeedback.destination_port_id, FclFreightRateFeedback.container_size, FclFreightRateFeedback.container_type, FclFreightRateFeedback.commodity).where(FclFreightRateFeedback.id==filters['similar_id'])).first()
    if feedback_data:
        query = query.where(FclFreightRateFeedback.id != filters.get('similar_id'))
        query = query.where(FclFreightRateFeedback.origin_port_id == feedback_data.origin_port_id, FclFreightRateFeedback.destination_port_id == feedback_data.destination_port_id, FclFreightRateFeedback.container_size == feedback_data.container_size, FclFreightRateFeedback.container_type == feedback_data.container_type, FclFreightRateFeedback.commodity == feedback_data.commodity)

    return query

def get_data(query, spot_search_details_required, booking_details_required):
    if not booking_details_required:
        query = query.select(
            FclFreightRateFeedback.id,
            FclFreightRateFeedback.cogo_entity_id,
            FclFreightRateFeedback.closed_by_id,
            FclFreightRateFeedback.closed_by,
            FclFreightRateFeedback.closing_remarks,
            FclFreightRateFeedback.created_at,
            FclFreightRateFeedback.fcl_freight_rate_id,
            FclFreightRateFeedback.feedback_type,
            FclFreightRateFeedback.feedbacks,
            FclFreightRateFeedback.outcome,
            FclFreightRateFeedback.outcome_object_id,
            FclFreightRateFeedback.performed_by_id,
            FclFreightRateFeedback.performed_by,
            FclFreightRateFeedback.performed_by_org_id,
            FclFreightRateFeedback.performed_by_org,
            FclFreightRateFeedback.performed_by_type,
            FclFreightRateFeedback.preferred_detention_free_days,
            FclFreightRateFeedback.preferred_freight_rate,
            FclFreightRateFeedback.preferred_freight_rate_currency,
            FclFreightRateFeedback.preferred_shipping_line_ids,
            FclFreightRateFeedback.preferred_shipping_lines,
            FclFreightRateFeedback.remarks,
            FclFreightRateFeedback.serial_id,
            FclFreightRateFeedback.source,
            FclFreightRateFeedback.source_id,
            FclFreightRateFeedback.status,
            FclFreightRateFeedback.updated_at,
            FclFreightRateFeedback.validity_id,
            FclFreightRateFeedback.origin_port_id,
            FclFreightRateFeedback.origin_continent_id,
            FclFreightRateFeedback.origin_trade_id,
            FclFreightRateFeedback.origin_country_id,
            FclFreightRateFeedback.destination_port_id,
            FclFreightRateFeedback.destination_continent_id,
            FclFreightRateFeedback.destination_trade_id,
            FclFreightRateFeedback.destination_country_id,
            FclFreightRateFeedback.commodity,
            FclFreightRateFeedback.container_size,
            FclFreightRateFeedback.container_type,
            FclFreightRateFeedback.service_provider_id,
            FclFreightRateFeedback.origin_port,
            FclFreightRateFeedback.destination_port
        )
    data = list(query.dicts())
    # fcl_freight_rate_ids = [row['fcl_freight_rate_id'] for row in data]

    # fcl_freight_rates = list(FclFreightRate.select(FclFreightRate.id,FclFreightRate.container_size,FclFreightRate.container_type,FclFreightRate.validities).where(FclFreightRate.id.in_(fcl_freight_rate_ids)).dicts())
    # fcl_freight_rate_mappings = {k['id']: k for k in fcl_freight_rates}
    service_provider_ids = []
    for item in data:
        if 'booking_params' in item and 'rate_card' in item['booking_params'] and item['booking_params']['rate_card'] and 'service_rates' in item['booking_params']['rate_card']:
            service_rates = item['booking_params']['rate_card']['service_rates'] or {}
            rates = service_rates.values()
            for rate in rates:
                if 'service_provider_id' in rate:
                    service_provider_ids.append(rate['service_provider_id'])
    service_providers = []
    service_providers_hash = {}
    if len(service_provider_ids):
        service_providers = get_organization(service_provider_ids)
        for sp in service_providers:
            service_providers_hash[sp['id']] = sp
    spot_search_hash = {}
    new_data = []
    if spot_search_details_required:
        spot_search_ids = list(set([str(row['source_id']) for row in data]))
        spot_search_data = spot_search.list_spot_searches({'filters':{'id': spot_search_ids}})['list']
        for search in spot_search_data:
            spot_search_hash[search['id']] = {'id':search.get('id'), 'importer_exporter_id':search.get('importer_exporter_id'), 'importer_exporter':search.get('importer_exporter'), 'service_details':search.get('service_details')}

    for object in data:
        # rate = fcl_freight_rate_mappings[object.get('fcl_freight_rate_id', None)] or {}
        # object['container_size'] = rate.get('container_size')
        # object['container_type'] = rate.get('container_type')
        # object['commodity'] = rate.get('commodity')
        if 'booking_params' in object:
            object['containers_count'] = object['booking_params'].get('containers_count', None)
            object['bls_count'] = object['booking_params'].get('bls_count', None)
            object['inco_term'] = object['booking_params'].get('inco_term', None)
        # try:
        #     price_currency = [t for t in object['validities'] if t['id'] == object.get('validity_id')][0]
        #     object['price'] = price_currency['price']
        #     object['currency'] = price_currency['currency']
        # except:
        #     object['price'] = None
        #     object['currency'] = None

        if object['booking_params'].get('rate_card', {}).get('service_rates', {}):
            for key, value in object['booking_params']['rate_card']['service_rates'].items():
                service_provider = value.get('service_provider_id', None)
                if service_provider:
                    value['service_provider'] = service_providers_hash.get(service_provider)
        if spot_search_details_required:
            object['spot_search'] = spot_search_hash.get(str(object['source_id']), {})
        new_data.append(object)
    return new_data

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

    query = FclFreightRateFeedback.select()

    if filters:
        if 'status' in filters:
            del filters['status']
        if 'closed_by_id' in filters:
            del filters['closed_by_id']

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)

        query = get_filters(direct_filters, query, FclFreightRateFeedback)
        query = apply_indirect_filters(query, indirect_filters)

    # query = get_join_query(query)
    query = (
        query
        .select(
            fn.count(FclFreightRateFeedback.id).over().alias('get_total'),
          fn.count(FclFreightRateFeedback.id).filter(FclFreightRateFeedback.status == 'active').over().alias('get_status_count_active'),
        fn.count(FclFreightRateFeedback.id).filter(FclFreightRateFeedback.status == 'inactive').over().alias('get_status_count_inactive'),
        fn.count(FclFreightRateFeedback.id).filter((FclFreightRateFeedback.status=='inactive') & (FclFreightRateFeedback.closed_by_id==performed_by_id)).over().alias('get_total_closed_by_user'),
        fn.count(FclFreightRateFeedback.id).filter((FclFreightRateFeedback.status=='active')  & (FclFreightRateFeedback.performed_by_id==performed_by_id)).over().alias('get_total_opened_by_user'),

         )
    ).limit(1)


    result = query.execute()
    if len(result)>0:
        result = result[0]
        stats = {
        'total': result.get_total,
        'total_closed_by_user': result.get_total_closed_by_user,
        'total_opened_by_user': result.get_total_opened_by_user,
        'total_open': result.get_status_count_active,
        'total_closed': result.get_status_count_inactive
        }
    else:
        stats = {}
    return { 'stats': stats }

# def get_total(query, performed_by_id):
#     try:
#         query = query.select(FclFreightRateFeedback.id)

#         return {'get_total':query.count()}
#     except:
#         return {'get_total' : 0}

# def get_total_closed_by_user(query, performed_by_id):
#     try:
#         query = query.select(FclFreightRateFeedback.id)

#         return {'get_total_closed_by_user':query.where(FclFreightRateFeedback.status == 'inactive', FclFreightRateFeedback.closed_by_id == performed_by_id).count() }
#     except:
#         return {'get_total_closed_by_user':0}


# def get_total_opened_by_user(query, performed_by_id):
#     try:
#         query = query.select(FclFreightRateFeedback.id)

#         return {'get_total_opened_by_user' : query.where(FclFreightRateFeedback.status == 'active', FclFreightRateFeedback.performed_by_id == performed_by_id).count() }
#     except:
#         return {'get_total_opened_by_user' : 0}

# def get_status_count(query, performed_by_id):
#     try:
#         query = query.select(FclFreightRateFeedback.status, fn.COUNT(SQL('*')).alias('count_all')).group_by(FclFreightRateFeedback.status)
#         result = {}
#         for row in query.execute():
#             result[row.status] = row.count_all
#         return {'get_status_count' : result}
#     except:
#         return {'get_status_count' : 0}
