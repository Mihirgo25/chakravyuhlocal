from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
from libs.json_encoder import json_encoder
import json
from services.fcl_customs_rate.models.fcl_customs_rate_feedback import FclCustomsRateFeedback
from services.fcl_customs_rate.models.fcl_customs_rate import FclCustomsRate
from database.rails_db import get_partner_user_experties, get_organization_service_experties
from datetime import datetime
from math import ceil
from peewee import fn, SQL,Window
from micro_services.client import spot_search
from database.rails_db import get_organization

possible_direct_filters = ['feedback_type', 'performed_by_org_id', 'performed_by_id', 'status', 'closed_by_id', 'country_id', 'trade_type', 'port_id', 'trade_id', 'service_provider_id']

possible_indirect_filters = ['relevant_supply_agent', 'validity_start_greater_than', 'validity_end_less_than', 'similar_id', 'supply_agent_id']

def list_fcl_customs_rate_feedbacks(filters = {}, spot_search_details_required=False, page_limit =10, page=1, performed_by_id=None, is_stats_required=True):
    query = FclCustomsRateFeedback.select()

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)

        query = get_filters(direct_filters, query, FclCustomsRateFeedback)
        query = apply_indirect_filters(query, indirect_filters)

    # query = get_join_query(query)
    stats = get_stats(filters, is_stats_required, performed_by_id) or {}
    pagination_data = get_pagination_data(query, page, page_limit)

    query = get_page(query, page, page_limit)
    data = get_data(query,spot_search_details_required) 

    return {'list': json_encoder(data) } | (pagination_data) | (stats)

def get_page(query, page, page_limit):
    query = query.order_by(FclCustomsRateFeedback.created_at.desc(nulls='LAST')).paginate(page, page_limit)
    return query

# def get_join_query(query):
#     query = query.join(FclCustomsRate, on=( FclCustomsRateFeedback.fcl_customs_rate_id == FclCustomsRate.id))
#     return query

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query

def apply_relevant_supply_agent_filter(query, filters):
    expertises = get_partner_user_experties('fcl_customs', filters['relevant_supply_agent'])
    location_id = [t['location_id'] for t in expertises]
    query = query.where((FclCustomsRateFeedback.location_id << location_id) |
                    (FclCustomsRateFeedback.country_id << location_id))
    return query

def apply_supply_agent_id_filter(query, filters):
    expertises = get_organization_service_experties('fcl_customs', filters['supply_agent_id'])
    location_id = [t['location_id'] for t in expertises]
    query = query.where((FclCustomsRateFeedback.location_id << location_id) |
                    (FclCustomsRateFeedback.country_id << location_id))
    return query

# def apply_country_id_filter(query, filters):
#     query = query.where(FclCustomsRateFeedback.country_id == filters['country_id'])
#     return query

# def apply_trade_type_filter(query, filters):
#     query = query.where(FclCustomsRateFeedback.trade_type == filters['trade_type'])
#     return query

# def apply_port_id_filter(query, filters):
#     query = query.where(FclCustomsRateFeedback.port_id == filters['port_id'])
#     return query

# def apply_trade_id_filter(query, filters):
#     query = query.where(FclCustomsRateFeedback.trade_id == filters['trade_id'])
#     return query

def apply_validity_start_greater_than_filter(query, filters):
    query = query.where(FclCustomsRateFeedback.created_at.cast('date') >= datetime.fromisoformat(filters['validity_start_greater_than']).date())
    return query

def apply_validity_end_less_than_filter(query, filters):
    query = query.where(FclCustomsRateFeedback.created_at.cast('date') <= datetime.fromisoformat(filters['validity_end_less_than']).date())
    return query

def apply_similar_id_filter(query, filters):
    feedback_data = (FclCustomsRateFeedback.select(FclCustomsRateFeedback.location_id, FclCustomsRateFeedback.commodity, FclCustomsRateFeedback.trade_type).where(FclCustomsRateFeedback.id==filters['similar_id'])).first()
    if feedback_data:
        query = query.where(FclCustomsRateFeedback.id != filters.get('similar_id'))
        query = query.where(FclCustomsRateFeedback.location_id == feedback_data.location_id, FclCustomsRateFeedback.commodity == feedback_data.commodity, FclCustomsRateFeedback.trade_type == feedback_data.trade_type)
    return query

def get_data(query, spot_search_details_required):
    data = list(query.dicts())

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
        if 'booking_params' in object:
            object['containers_count'] = object['booking_params'].get('containers_count', None)
            object['bls_count'] = object['booking_params'].get('bls_count', None)
            object['inco_term'] = object['booking_params'].get('inco_term', None)

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

    query = FclCustomsRateFeedback.select()

    if filters:
        if 'status' in filters:
            del filters['status']
        if 'closed_by_id' in filters:
            del filters['closed_by_id']

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)

        query = get_filters(direct_filters, query, FclCustomsRateFeedback)
        query = apply_indirect_filters(query, indirect_filters)

    # query = get_join_query(query)
    query = (
        query
        .select(
            fn.count(FclCustomsRateFeedback.id).over().alias('get_total'),
            fn.count(FclCustomsRateFeedback.id).filter(FclCustomsRateFeedback.status == 'active').over().alias('get_status_count_active'),
            fn.count(FclCustomsRateFeedback.id).filter(FclCustomsRateFeedback.status == 'inactive').over().alias('get_status_count_inactive'),
            fn.count(FclCustomsRateFeedback.id).filter((FclCustomsRateFeedback.status=='inactive') & (FclCustomsRateFeedback.closed_by_id==performed_by_id)).over().alias('get_total_closed_by_user'),
            fn.count(FclCustomsRateFeedback.id).filter((FclCustomsRateFeedback.status=='active')  & (FclCustomsRateFeedback.performed_by_id==performed_by_id)).over().alias('get_total_opened_by_user'),
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
    return {'stats': stats }

def get_total(query, performed_by_id):
    try:
        query = query.select(FclCustomsRateFeedback.id)

        return {'get_total':query.count()}
    except:
        return {'get_total' : 0}

def get_total_closed_by_user(query, performed_by_id):
    try:
        query = query.select(FclCustomsRateFeedback.id)

        return {'get_total_closed_by_user':query.where(FclCustomsRateFeedback.status == 'inactive', FclCustomsRateFeedback.closed_by_id == performed_by_id).count() }
    except:
        return {'get_total_closed_by_user':0}


def get_total_opened_by_user(query, performed_by_id):
    try:
        query = query.select(FclCustomsRateFeedback.id)

        return {'get_total_opened_by_user' : query.where(FclCustomsRateFeedback.status == 'active', FclCustomsRateFeedback.performed_by_id == performed_by_id).count() }
    except:
        return {'get_total_opened_by_user' : 0}

def get_status_count(query, performed_by_id):
    try:
        query = query.select(FclCustomsRateFeedback.status, fn.COUNT(SQL('*')).alias('count_all')).group_by(FclCustomsRateFeedback.status)
        result = {}
        for row in query.execute():
            result[row.status] = row.count_all
        return {'get_status_count' : result}
    except:
        return {'get_status_count' : 0}