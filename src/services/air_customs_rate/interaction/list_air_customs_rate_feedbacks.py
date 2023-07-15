from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
from libs.json_encoder import json_encoder
import json
from services.air_customs_rate.models.air_customs_rate_feedback import AirCustomsRateFeedback
from database.rails_db import get_partner_user_experties
from datetime import datetime
from math import ceil
from peewee import fn
from micro_services.client import spot_search
from database.rails_db import get_organization

possible_direct_filters = ['feedback_type', 'performed_by_org_id', 'performed_by_id', 'status', 'closed_by_id', 'country_id', 'trade_type', 'service_provider_id', 'airport_id']

possible_indirect_filters = ['relevant_supply_agent', 'validity_start_greater_than', 'validity_end_less_than', 'similar_id']

def list_air_customs_rate_feedbacks(filters = {}, spot_search_details_required=False, customer_details_required=False, page_limit =10, page=1, performed_by_id=None, is_stats_required=True):
    query = AirCustomsRateFeedback.select()

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)

        query = get_filters(direct_filters, query, AirCustomsRateFeedback)
        query = apply_indirect_filters(query, indirect_filters)

    stats = get_stats(filters, is_stats_required, performed_by_id) or {}
    pagination_data = get_pagination_data(query, page, page_limit)

    query = get_page(query, page, page_limit)
    data = get_data(query,spot_search_details_required,customer_details_required)

    return {'list': json_encoder(data) } | (pagination_data) | (stats)

def get_page(query, page, page_limit):
    query = query.order_by(AirCustomsRateFeedback.created_at.desc(nulls='LAST')).paginate(page, page_limit)
    return query

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query

def apply_relevant_supply_agent_filter(query, filters):
    expertises = get_partner_user_experties('air_customs', filters['relevant_supply_agent'])
    location_id = [t['location_id'] for t in expertises]
    query = query.where((AirCustomsRateFeedback.airport_id << location_id) |
                    (AirCustomsRateFeedback.continent_id << location_id) |
                    (AirCustomsRateFeedback.city_id << location_id) |
                    (AirCustomsRateFeedback.country_id << location_id))
    return query

def apply_validity_start_greater_than_filter(query, filters):
    query = query.where(AirCustomsRateFeedback.created_at.cast('date') >= datetime.fromisoformat(filters['validity_start_greater_than'].split('T')[0]).date())
    return query

def apply_validity_end_less_than_filter(query, filters):
    query = query.where(AirCustomsRateFeedback.created_at.cast('date') <= datetime.fromisoformat(filters['validity_end_less_than'].split('T')[0]).date())
    return query

def apply_similar_id_filter(query, filters):
    feedback_data = (AirCustomsRateFeedback.select(AirCustomsRateFeedback.airport_id, AirCustomsRateFeedback.commodity, AirCustomsRateFeedback.trade_type).where(AirCustomsRateFeedback.id==filters['similar_id'])).first()
    if feedback_data:
        query = query.where(AirCustomsRateFeedback.id != filters.get('similar_id'))
        query = query.where(AirCustomsRateFeedback.airport_id == feedback_data.airport_id, AirCustomsRateFeedback.commodity == feedback_data.commodity, AirCustomsRateFeedback.trade_type == feedback_data.trade_type)
    return query

def get_data(query, spot_search_details_required, customer_details_required):
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
            if customer_details_required:
                spot_search_hash[search['id']] = {'id':search.get('id'), 'importer_exporter_id':search.get('importer_exporter_id'), 'importer_exporter':search.get('importer_exporter')}
            else:
                spot_search_hash[search['id']] = {'id':search.get('id'), 'service_details':search.get('service_details')}

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

    query = AirCustomsRateFeedback.select()

    if filters:
        if 'status' in filters:
            del filters['status']
        if 'closed_by_id' in filters:
            del filters['closed_by_id']

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)

        query = get_filters(direct_filters, query, AirCustomsRateFeedback)
        query = apply_indirect_filters(query, indirect_filters)

    query = (
        query
        .select(
            fn.count(AirCustomsRateFeedback.id).over().alias('get_total'),
            fn.count(AirCustomsRateFeedback.id).filter(AirCustomsRateFeedback.status == 'active').over().alias('get_status_count_active'),
            fn.count(AirCustomsRateFeedback.id).filter(AirCustomsRateFeedback.status == 'inactive').over().alias('get_status_count_inactive'),
            fn.count(AirCustomsRateFeedback.id).filter((AirCustomsRateFeedback.status=='inactive') & (AirCustomsRateFeedback.closed_by_id==performed_by_id)).over().alias('get_total_closed_by_user'),
            fn.count(AirCustomsRateFeedback.id).filter((AirCustomsRateFeedback.status=='active')  & (AirCustomsRateFeedback.performed_by_id==performed_by_id)).over().alias('get_total_opened_by_user'),
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