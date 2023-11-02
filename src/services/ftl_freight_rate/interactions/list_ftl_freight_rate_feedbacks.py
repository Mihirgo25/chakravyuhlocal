from services.ftl_freight_rate.models.ftl_freight_rate_feedback import FtlFreightRateFeedback
from services.ftl_freight_rate.models.ftl_freight_rate import FtlFreightRate
from playhouse.shortcuts import model_to_dict
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
from fastapi.encoders import jsonable_encoder
from libs.json_encoder import json_encoder
from database.rails_db import get_partner_user_experties, get_organization_service_experties
from datetime import datetime
import concurrent.futures, json
from peewee import fn, SQL,Window
from math import ceil
from micro_services.client import spot_search, partner
from database.rails_db import get_organization

possible_direct_filters = ['id', 'feedback_type', 'performed_by_id', 'closed_by_id', 'status', 'origin_location_id', 'destination_location_id', 'origin_country_id', 'destination_country_id', 'service_provider_id', 'serial_id']
possible_indirect_filters = ['relevant_supply_agent', 'validity_start_greater_than', 'validity_end_less_than', 'similar_id']

def list_ftl_freight_rate_feedbacks(filters = {}, includes = {}, spot_search_details_required=False, page_limit =10, page=1, performed_by_id=None, is_stats_required=True):
    query = get_query(includes)

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)

        query = get_filters(direct_filters, query, FtlFreightRateFeedback)
        query = apply_indirect_filters(query, indirect_filters)

    stats = get_stats(filters, is_stats_required, performed_by_id) or {}
    pagination_data = get_pagination_data(query, page, page_limit)

    query = get_page(query, page, page_limit)
    data = get_data(query,spot_search_details_required)

    return {'list': jsonable_encoder(data) } | (pagination_data) | (stats)

def get_query(includes):
    if includes and  not isinstance(includes, dict):
        includes = json.loads(includes)

    ftl_feedback_all_fields = list(FtlFreightRateFeedback._meta.fields.keys())
    required_ftl_feedback_fields = [a for a in includes.keys() if a in ftl_feedback_all_fields] if includes else ftl_feedback_all_fields
    ftl_feedback_fields = [getattr(FtlFreightRateFeedback, key) for key in required_ftl_feedback_fields]

    query = FtlFreightRateFeedback.select(*ftl_feedback_fields)

    return query

def get_page(query, page, page_limit):
    query = query.order_by(FtlFreightRateFeedback.created_at.desc(nulls='LAST')).paginate(page, page_limit)
    return query

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query

def apply_relevant_supply_agent_filter(query, filters):
    expertises = get_partner_user_experties('ftl_freight', filters['relevant_supply_agent'])
    origin_location_id = [t['origin_location_id'] for t in expertises]
    destination_location_id = [t['destination_location_id'] for t in expertises]

    query = query.where((FtlFreightRateFeedback.origin_location_id << origin_location_id)|
                        (FtlFreightRateFeedback.origin_country_id << origin_location_id))

    query = query.where((FtlFreightRateFeedback.destination_location_id <<destination_location_id)|
                        (FtlFreightRateFeedback.destination_country_id << destination_location_id))
    return query

def apply_validity_start_greater_than_filter(query, filters):
    query = query.where(FtlFreightRateFeedback.created_at.cast('date') >= datetime.fromisoformat(filters['validity_start_greater_than']).date())
    return query

def apply_validity_end_less_than_filter(query, filters):
    query = query.where(FtlFreightRateFeedback.created_at.cast('date') <= datetime.fromisoformat(filters['validity_end_less_than']).date())
    return query

def apply_similar_id_filter(query, filters):
    feedback_data = (FtlFreightRateFeedback.select().where(FtlFreightRateFeedback.id==filters['similar_id'])).first()
    if feedback_data:
        query = query.where(FtlFreightRateFeedback.id != filters.get('similar_id'))
        query = query.where(FtlFreightRateFeedback.origin_location_id == feedback_data.origin_location_id, FtlFreightRateFeedback.destination_location_id == feedback_data.destination_location_id)

    return query

def get_data(query, spot_search_details_required):
    data = json_encoder(list(query.dicts()))

    ftl_freight_rate_ids = []
    for rate in data:
        if rate['ftl_freight_rate_id']:
            ftl_freight_rate_ids.append((rate['ftl_freight_rate_id']))
        if rate.get('reverted_rate_id'):
            ftl_freight_rate_ids.append((rate['reverted_rate_id']))
    ftl_freight_rates = FtlFreightRate.select(FtlFreightRate.id,
                                            FtlFreightRate.origin_location,
                                            FtlFreightRate.destination_location,
                                            FtlFreightRate.commodity,
                                            FtlFreightRate.line_items,
            ).where(FtlFreightRate.id.in_(ftl_freight_rate_ids))
    ftl_freight_rates = json_encoder(list(ftl_freight_rates.dicts()))
    ftl_freight_rate_mappings = {k['id']: k for k in ftl_freight_rates}

    service_provider_ids = []
    for object in data:
        service_provider_ids.append(object.get('service_provider_id'))

    service_providers = []
    service_providers_hash = {}
    if len(service_provider_ids):
        service_providers = get_organization(service_provider_ids)
        for sp in service_providers:
            service_providers_hash[sp['id']] = sp

    spot_search_hash = {}
    new_data = []
    if spot_search_details_required:
        spot_search_ids = list(set([str(row.get('source_id')) for row in data]))
        spot_search_data = spot_search.list_spot_searches({'filters':{'id': spot_search_ids}})['list']
        for search in spot_search_data:
            spot_search_hash[search['id']] = {'id':search.get('id'), 'importer_exporter_id':search.get('importer_exporter_id'), 'importer_exporter':search.get('importer_exporter'), 'service_details':search.get('service_details')}

    for object in data:
        rate = ftl_freight_rate_mappings.get((object.get('ftl_freight_rate_id')))
        if rate:
            object["origin_location"] = rate.get("origin_location")
            object["destination_location"] = rate.get("destination_location")
            object["commodity"] = rate.get("commodity")
            object["price"] = sum(int(p['price']) for p in rate.get("line_items")) if rate.get("line_items") else None
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

    query = FtlFreightRateFeedback.select()

    if filters:
        if 'status' in filters:
            del filters['status']
        if 'closed_by_id' in filters:
            del filters['closed_by_id']

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)

        query = get_filters(direct_filters, query, FtlFreightRateFeedback)
        query = apply_indirect_filters(query, indirect_filters)

    query = (
        query
        .select(
            fn.count(FtlFreightRateFeedback.id).over().alias('get_total'),
          fn.count(FtlFreightRateFeedback.id).filter(FtlFreightRateFeedback.status == 'active').over().alias('get_status_count_active'),
        fn.count(FtlFreightRateFeedback.id).filter(FtlFreightRateFeedback.status == 'inactive').over().alias('get_status_count_inactive'),
        fn.count(FtlFreightRateFeedback.id).filter((FtlFreightRateFeedback.status=='inactive') & (FtlFreightRateFeedback.closed_by_id==performed_by_id)).over().alias('get_total_closed_by_user'),
        fn.count(FtlFreightRateFeedback.id).filter((FtlFreightRateFeedback.status=='active')  & (FtlFreightRateFeedback.performed_by_id==performed_by_id)).over().alias('get_total_opened_by_user'),

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
