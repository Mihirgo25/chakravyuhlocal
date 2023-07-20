from services.haulage_freight_rate.models.haulage_freight_rate_feedback import HaulageFreightRateFeedback
from libs.get_filters import get_filters
from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
from libs.get_applicable_filters import get_applicable_filters
from libs.json_encoder import json_encoder
from database.rails_db import get_partner_user_experties
from datetime import datetime
import json
from peewee import fn
from math import ceil
from micro_services.client import spot_search
from database.rails_db import get_organization
from libs.json_encoder import json_encoder


possible_direct_filters = ['feedback_type','performed_by_id','status','closed_by_id','origin_location_id', 'destination_location_id', 'origin_country_id', 'destination_country_id', 'service_provider_id']
possible_indirect_filters = ['relevant_supply_agent','validity_start_greater_than','validity_end_less_than','similar_id']

def list_haulage_freight_rate_feedbacks(filters = {},spot_search_details_required=False, page_limit =10, page=1, performed_by_id=None, is_stats_required=True, booking_details_required=False):
    query = HaulageFreightRateFeedback.select()

    # apply direct and indirect filter
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)

        query = get_filters(direct_filters, query, HaulageFreightRateFeedback)
        query = apply_indirect_filters(query, indirect_filters)

    # get required stats
    stats = get_stats(filters, is_stats_required, performed_by_id) or {}

    # get pagination data
    pagination_data = get_pagination_data(query, page, page_limit)

    # paginate
    query = get_page(query, page, page_limit)

    # get data
    data = get_data(query,spot_search_details_required,booking_details_required) 

    return {'list': json_encoder(data) } | (pagination_data) | (stats)

def get_page(query, page, page_limit):
    query = query.order_by(HaulageFreightRateFeedback.created_at.desc(nulls='LAST')).paginate(page, page_limit)
    return query

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query


def apply_relevant_supply_agent_filter(query, filters):
    expertises = get_partner_user_experties('haulage_freight', filters['relevant_supply_agent'])
    origin_location_id = [t['origin_location_id'] for t in expertises]
    destination_location_id = [t['destination_location_id'] for t in expertises]
    query = query.where(((HaulageFreightRateFeedback.origin_location_id << origin_location_id) | 
                        (HaulageFreightRateFeedback.origin_city_id << origin_location_id) | 
                        (HaulageFreightRateFeedback.origin_country_id << origin_location_id)))
    
    query = query.where(((HaulageFreightRateFeedback.destination_location_id <<destination_location_id) | 
                        (HaulageFreightRateFeedback.destination_city_id << destination_location_id) | 
                        (HaulageFreightRateFeedback.origin_country_id << destination_location_id)))
    return query

def apply_validity_start_greater_than_filter(query, filters):
    query = query.where(HaulageFreightRateFeedback.created_at.cast('date') >= datetime.fromisoformat(filters['validity_start_greater_than']).date())
    return query

def apply_validity_end_less_than_filter(query, filters):
    query = query.where(HaulageFreightRateFeedback.created_at.cast('date') <= datetime.fromisoformat(filters['validity_end_less_than']).date())
    return query


def apply_similar_id_filter(query, filters):
    feedback_data = (HaulageFreightRateFeedback.select(HaulageFreightRateFeedback.origin_location_id, HaulageFreightRateFeedback.destination_location_id, HaulageFreightRateFeedback.container_size, HaulageFreightRateFeedback.container_type, HaulageFreightRateFeedback.commodity).where(HaulageFreightRateFeedback.id==filters['similar_id'])).first()
    if feedback_data:
        query = query.where(HaulageFreightRateFeedback.id != filters.get('similar_id'))
        query = query.where(HaulageFreightRateFeedback.origin_location_id == feedback_data.origin_location_id, HaulageFreightRateFeedback.destination_location_id == feedback_data.destination_location_id, HaulageFreightRateFeedback.container_size == feedback_data.container_size, HaulageFreightRateFeedback.container_type == feedback_data.container_type, HaulageFreightRateFeedback.commodity == feedback_data.commodity)
    return query

def get_data(query, spot_search_details_required, booking_details_required):
    if not booking_details_required:
        query = query.select()
    data = json_encoder(list(query.dicts()))
    haulage_freight_rate_ids = []
    for rate in data:
        if rate['haulage_freight_rate_id']:
            haulage_freight_rate_ids.append((rate['haulage_freight_rate_id']))
        if rate.get('reverted_rate_id'):
            haulage_freight_rate_ids.append((rate['reverted_rate_id']))
    haulage_freight_rates = HaulageFreightRate.select(HaulageFreightRate.id,
                                            HaulageFreightRate.origin_location,
                                            HaulageFreightRate.destination_location,
                                            HaulageFreightRate.commodity,
                                            HaulageFreightRate.line_items,
            ).where(HaulageFreightRate.id.in_(haulage_freight_rate_ids))
    haulage_freight_rates = json_encoder(list(haulage_freight_rates.dicts()))
    haulage_freight_rate_mappings = {k['id']: k for k in haulage_freight_rates}

    service_provider_ids = []
    for object in data:
        service_provider_ids.append(object.get('service_provider_id'))
    service_providers = []
    service_providers_hash = {}
    if len(service_provider_ids):
        service_providers = get_organization(service_provider_ids)
        for service_provider in service_providers:
            service_providers_hash[service_provider['id']] = service_provider
    spot_search_hash = {}
    new_data = []
    if spot_search_details_required:
        spot_search_ids = list(set([str(row['source_id']) for row in data]))
        spot_search_data = spot_search.list_spot_searches({'filters':{'id': spot_search_ids}})['list']
        for search in spot_search_data:
            spot_search_hash[search['id']] = {'id':search.get('id'), 'importer_exporter_id':search.get('importer_exporter_id'), 'importer_exporter':search.get('importer_exporter'), 'service_details':search.get('service_details')}

    for object in data:
        rate = haulage_freight_rate_mappings.get((object.get('haulage_freight_rate_id')))
        if rate:
            object["origin_location"] = rate.get("origin_location")
            object["destination_location"] = rate.get("destination_location")
            object["commodity"] = rate.get("commodity")
            object["price"] = sum(p['price'] for p in rate.get("line_items")) if rate.get("line_items") else None
            object["currency"] = rate["line_items"][0].get('currency') if rate["line_items"] else None
        service_provider = object.get('service_provider_id', None)
        if service_provider:
            object['service_provider'] = service_providers_hash.get(service_provider)
        organization_id = object.get('performed_by_org_id', None)
        if organization_id:
            object['organization'] = service_providers_hash.get(organization_id)
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

    query = HaulageFreightRateFeedback.select()

    if filters:
        if 'status' in filters:
            del filters['status']
        if 'closed_by_id' in filters:
            del filters['closed_by_id']

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)

        query = get_filters(direct_filters, query, HaulageFreightRateFeedback)
        query = apply_indirect_filters(query, indirect_filters)
    query = (
        query
        .select(
            fn.count(HaulageFreightRateFeedback.id).over().alias('get_total'),
          fn.count(HaulageFreightRateFeedback.id).filter(HaulageFreightRateFeedback.status == 'active').over().alias('get_status_count_active'),
        fn.count(HaulageFreightRateFeedback.id).filter(HaulageFreightRateFeedback.status == 'inactive').over().alias('get_status_count_inactive'),
        fn.count(HaulageFreightRateFeedback.id).filter((HaulageFreightRateFeedback.status=='inactive') & (HaulageFreightRateFeedback.closed_by_id==performed_by_id)).over().alias('get_total_closed_by_user'),
        fn.count(HaulageFreightRateFeedback.id).filter((HaulageFreightRateFeedback.status=='active')  & (HaulageFreightRateFeedback.performed_by_id==performed_by_id)).over().alias('get_total_opened_by_user'),

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
