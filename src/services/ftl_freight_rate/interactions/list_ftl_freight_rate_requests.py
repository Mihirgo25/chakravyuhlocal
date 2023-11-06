from services.ftl_freight_rate.models.ftl_freight_rate_request import FtlFreightRateRequest
from fastapi.encoders import jsonable_encoder
from math import ceil
from datetime import datetime
from peewee import fn
import json
from database.rails_db import get_organization_service_experties,get_organization, get_partner_user_experties
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
from micro_services.client import spot_search
from libs.json_encoder import json_encoder

possible_indirect_filters = ['relevant_supply_agent', 'validity_start_greater_than', 'validity__less_than', 'similar_id', 'q']
possible_direct_filters = ['id', 'origin_location_id','serial_id','destination_location_id', 'performed_by_id', 'status', 'closed_by_id', 'origin_country_id', 'destination_country_id', 'id']

def list_ftl_freight_rate_requests(filters, page_limit, page, sort_by, sort_type,is_stats_required,spot_search_details_required,performed_by_id, includes = {}):
    query = get_query(sort_by, sort_type, includes)

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
        query = get_filters(direct_filters, query, FtlFreightRateRequest)
        query = apply_indirect_filters(query, indirect_filters)

    stats = get_stats(filters, is_stats_required, performed_by_id) or {}

    pagination_data = get_pagination_data(query, page, page_limit)

    query = get_page(query, page, page_limit)

    data = get_data(query,spot_search_details_required)

    return {'list': jsonable_encoder(data) } | (pagination_data) | (stats)

def get_query(sort_by, sort_type, includes):
    if includes and  not isinstance(includes, dict):
        includes = json.loads(includes)

    ftl_request_all_fields = list(FtlFreightRateRequest._meta.fields.keys())
    required_ftl_request_fields = [a for a in includes.keys() if a in ftl_request_all_fields] if includes else ftl_request_all_fields
    ftl_request_fields = [getattr(FtlFreightRateRequest, key) for key in required_ftl_request_fields]

    query = FtlFreightRateRequest.select(*ftl_request_fields).order_by(eval("FtlFreightRateRequest.{}.{}()".format(sort_by, sort_type)))
    return query


def apply_pagination(query, page, page_limit):
    offset = (page - 1) * page_limit
    total_count = query.count()
    query = query.offset(offset).limit(page_limit)
    return query, total_count

def get_page(query, page, page_limit):
    return query.order_by(FtlFreightRateRequest.created_at.desc()).paginate(page, page_limit)


def get_pagination_data(query, page, page_limit):
    total_count = query.count()
    pagination_data = {
        'page': page,
        'total': ceil(total_count/page_limit),
        'total_count': total_count,
        'page_limit': page_limit
        }
    return pagination_data

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query

def apply_validity_start_greater_than_filter(query, filters):
    return query.where(FtlFreightRateRequest.created_at.cast('date') >= datetime.fromisoformat(filters['validity_start_greater_than']).date())

def apply_validity_end_less_than_filter(query, filters):
    return query.where(FtlFreightRateRequest.created_at.cast('date') <= datetime.fromisoformat(filters['validity_end_less_than']).date())

def apply_q_filter(query, filters):
    q = str(filters.get('q', ''))
    query = query.where(FtlFreightRateRequest.serial_id.cast("text") ** (q + "%"))
    return query

def apply_relevant_supply_agent_filter(query, filters):
    expertises = get_partner_user_experties('ftl_freight', filters['relevant_supply_agent'])
    origin_location_id = [t['origin_location_id'] for t in expertises]
    destination_location_id = [t['destination_location_id'] for t in expertises]

    query = query.where((FtlFreightRateRequest.origin_location_id << origin_location_id)|
                        (FtlFreightRateRequest.origin_country_id << origin_location_id)|
                        (FtlFreightRateRequest.origin_city_id << origin_location_id))

    query = query.where((FtlFreightRateRequest.destination_location_id <<destination_location_id)|
                        (FtlFreightRateRequest.destination_country_id << destination_location_id)|
                        (FtlFreightRateRequest.destination_city_id << destination_location_id))
    return query

def apply_supply_agent_id_filter(query, filters):
    expertises = get_organization_service_experties('ftl_freight', filters['supply_agent_id'])
    origin_location_id = [t['origin_location_id'] for t in expertises]
    destination_location_id =  [t['destination_location_id'] for t in expertises]
    query = query.where((FtlFreightRateRequest.origin_location_id << origin_location_id) | (FtlFreightRateRequest.origin_country_id << origin_location_id) | (FtlFreightRateRequest.origin_continent_id << origin_location_id) | (FtlFreightRateRequest.origin_trade_id << origin_location_id))
    query = query.where((FtlFreightRateRequest.destination_location_id << destination_location_id) | (FtlFreightRateRequest.destination_country_id << destination_location_id) | (FtlFreightRateRequest.destination_continent_id << destination_location_id) | (FtlFreightRateRequest.destination_trade_id << destination_location_id))
    return query

def apply_service_provider_id_filter(query, filters):
    expertises = get_organization_service_experties('ftl_freight', filters['service_provider_id'], account_type='organization')
    origin_location_id = [t['origin_location_id'] for t in expertises]
    destination_location_id =  [t['destination_location_id'] for t in expertises]
    query = query.where((FtlFreightRateRequest.origin_location_id << origin_location_id) | (FtlFreightRateRequest.origin_country_id << origin_location_id) | (FtlFreightRateRequest.origin_continent_id << origin_location_id) | (FtlFreightRateRequest.origin_trade_id << origin_location_id))
    query = query.where((FtlFreightRateRequest.destination_location_id << destination_location_id) | (FtlFreightRateRequest.destination_country_id << destination_location_id) | (FtlFreightRateRequest.destination_continent_id << destination_location_id) | (FtlFreightRateRequest.destination_trade_id << destination_location_id))
    return query

def apply_similar_id_filter(query,filters):
    rate_request_obj = FtlFreightRateRequest.select(FtlFreightRateRequest.origin_location_id, FtlFreightRateRequest.destination_location_id, FtlFreightRateRequest.truck_type, FtlFreightRateRequest.commodity).where(FtlFreightRateRequest.id == filters['similar_id']).dicts().get()
    query = query.where(FtlFreightRateRequest.id != filters['similar_id'])
    return query.where(FtlFreightRateRequest.origin_location_id == rate_request_obj['origin_location_id'], FtlFreightRateRequest.destination_location_id == rate_request_obj['destination_location_id'], FtlFreightRateRequest.truck_type == rate_request_obj['truck_type'], FtlFreightRateRequest.commodity == rate_request_obj['commodity'])

def get_stats(filters, is_stats_required, performed_by_id):
    if not is_stats_required:
        return {}

    query = FtlFreightRateRequest.select()

    if filters:
        if 'status' in filters:
            del filters['status']
        if 'closed_by_id' in filters:
            del filters['closed_by_id']

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)

        query = get_filters(direct_filters, query, FtlFreightRateRequest)
        query = apply_indirect_filters(query, indirect_filters)

    query = (
        query
        .select(
            fn.count(FtlFreightRateRequest.id).over().alias('get_total'),
          fn.count(FtlFreightRateRequest.id).filter(FtlFreightRateRequest.status == 'active').over().alias('get_status_count_active'),
        fn.count(FtlFreightRateRequest.id).filter(FtlFreightRateRequest.status == 'inactive').over().alias('get_status_count_inactive'),
        fn.count(FtlFreightRateRequest.id).filter((FtlFreightRateRequest.status=='inactive') & (FtlFreightRateRequest.closed_by_id==performed_by_id)).over().alias('get_total_closed_by_user'),
        fn.count(FtlFreightRateRequest.id).filter((FtlFreightRateRequest.status=='active')  & (FtlFreightRateRequest.performed_by_id==performed_by_id)).over().alias('get_total_opened_by_user'),

         )
    ).limit(1)
    result = query.execute()

    if len(result)>0:
        result =result[0]
        stats = {
        'total': result.get_total,
        'total_closed_by_user': result.get_total_closed_by_user,
        'total_opened_by_user': result.get_total_opened_by_user,
        'total_open': result.get_status_count_active,
        'total_closed': result.get_status_count_inactive
        }
    else:
        stats ={}
    return { 'stats': stats }

def get_data(query, spot_search_details_required):
    data = json_encoder(list(query.dicts()))

    service_provider_ids = []
    for item in data:
        if item.get('booking_params') and item.get('booking_pramas').get('rate_card') and 'service_rates' in item.get('booking_params').get('rate_card').keys():
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
        try:
            spot_search_data = spot_search.list_spot_searches({'filters':{'id': spot_search_ids}})['list']
        except:
            spot_search_data = []

        for search in spot_search_data:
            spot_search_hash[search['id']] = {'id':search.get('id'), 'importer_exporter_id':search.get('importer_exporter_id'), 'importer_exporter':search.get('importer_exporter'), 'service_details':search.get('service_details')}

    for object in data:
        if object.get('booking_params'):
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
