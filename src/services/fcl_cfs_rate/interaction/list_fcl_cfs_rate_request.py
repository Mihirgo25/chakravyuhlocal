from services.fcl_cfs_rate.models.fcl_cfs_rate_request import FclCfsRateRequest
from database.rails_db import get_partner_user_experties, get_organization_service_experties
from peewee import *
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
import json
POSSIBLE_INDIRECT_FILTERS = ['relevant_supply_agent', 'validity_start_greater_than', 'validity_end_less_than', 'similar_id', 'supply_agent_id']
POSSIBLE_DIRECT_FILTERS = ['port_id', 'performed_by_id', 'status', 'closed_by_id', 'trade_type', 'country_id']

def list_fcl_cfs_rate_request(filters, page_limit=10, page=1, is_stats_required=True, performed_by_id=None):
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)
        query = FclCfsRateRequest.select()
        query = apply_direct_filters(query, filters)
        query = apply_indirect_filters(query, filters)
    stats = get_stats(filters, is_stats_required, performed_by_id)
    # query = get_page(query, page, page_limit)
    data = get_data(query)
    # pagination_data = get_pagination_data(query, page, page_limit)
    response_data = {'list': data}
    # response_data.update(pagination_data)
    response_data.update(stats)

def get_page(query, page, page_limit):
    return query.order_by(FclCfsRateRequest.created_at.desc()).paginate(page, page_limit)

def apply_direct_filters(query, filters):
    direct_filters = {k: v for k, v in filters.items() if k in POSSIBLE_DIRECT_FILTERS}
    for k, v in direct_filters.items():
        query = query.where(getattr(FclCfsRateRequest, k) == v)
    return query


def apply_indirect_filters(query, filters):
    indirect_filters = {k: v for k, v in filters.items() if k in POSSIBLE_INDIRECT_FILTERS}
    for key in indirect_filters.keys():
        query = getattr(query, f"apply_{key}_filter")(filters)
    return query

def apply_validity_start_greater_than_filter(query, filters):
    return query.where(FclCfsRateRequest.created_at.date() >= filters['validity_start_greater_than'])

def apply_validity_end_less_than_filter(query, filters):
    return query.where(FclCfsRateRequest.created_at.date() <= filters['validity_end_less_than'])

def apply_relevant_supply_agent_filter(query, filters):
    expertises = get_partner_user_experties('fcl_freight', filters['relevant_supply_agent'])
    origin_port_id = [t['origin_location_id'] for t in expertises]
    destination_port_id =  [t['destination_location_id'] for t in expertises]
    query = query.where((FclCfsRateRequest.origin_port_id << origin_port_id) | (FclCfsRateRequest.origin_country_id << origin_port_id) | (FclCfsRateRequest.origin_continent_id << origin_port_id) | (FclCfsRateRequest.origin_trade_id << origin_port_id))
    query = query.where((FclCfsRateRequest.destination_port_id << destination_port_id) | (FclCfsRateRequest.destination_country_id << destination_port_id) | (FclCfsRateRequest.destination_continent_id << destination_port_id) | (FclCfsRateRequest.destination_trade_id << destination_port_id))
    return query

def apply_supply_agent_id_filter(query, filters):
    expertises = get_organization_service_experties('fcl_freight', filters['supply_agent_id'])
    origin_port_id = [t['origin_location_id'] for t in expertises]
    destination_port_id =  [t['destination_location_id'] for t in expertises]
    query = query.where((FclCfsRateRequest.origin_port_id << origin_port_id) | (FclCfsRateRequest.origin_country_id << origin_port_id) | (FclCfsRateRequest.origin_continent_id << origin_port_id) | (FclCfsRateRequest.origin_trade_id << origin_port_id))
    query = query.where((FclCfsRateRequest.destination_port_id << destination_port_id) | (FclCfsRateRequest.destination_country_id << destination_port_id) | (FclCfsRateRequest.destination_continent_id << destination_port_id) | (FclCfsRateRequest.destination_trade_id << destination_port_id))
    return query
    

def apply_similar_id_filter(query, filters):
    rate_request_obj = FclCfsRateRequest.get(FclCfsRateRequest.id == filters['similar_id'])
    query = query.where(FclCfsRateRequest.id != filters['similar_id'])
    query = query.where(
        (FclCfsRateRequest.port_id == rate_request_obj.port_id) &
        (FclCfsRateRequest.container_size == rate_request_obj.container_size) &
        (FclCfsRateRequest.container_type == rate_request_obj.container_type) &
        (FclCfsRateRequest.commodity == rate_request_obj.commodity) &
        (FclCfsRateRequest.inco_term == rate_request_obj.inco_term)
    )
    return query

def get_data(query):
    data = query.dicts().execute()
    add_service_objects(data)
    return data

def add_service_objects(data):
    objects = [
        {
            'name': 'user',
            'filters': {'id': list(set([d['performed_by_id'] for d in data] + [d['closed_by_id'] for d in data]))},
            'fields': ['id', 'name', 'email', 'mobile_country_code', 'mobile_number']
        },
        {
            'name': 'location',
            'filters': {'id': list(set([d['port_id'] for d in data]))},
            'fields': ['id', 'name', 'display_name', 'port_code', 'type']
        },
        {
            'name': 'spot_search',
            'filters': {'id': list(set([d['source_id'] for d in data]))},
            'fields': ['id', 'importer_exporter_id', 'importer_exporter', 'service_details']
        }
    ]
    """
     Has to make changes here but first testing the other apis so i will do this later.

    # """
    # service_objects = get_multiple_service_objects(objects)

    # for obj in data:
    #     obj['location'] = service_objects['location'].get(obj['port_id'], None)
    #     obj['performed_by'] = service_objects['user'].get(obj['performed_by_id'], None)
    #     obj['closed_by'] = service_objects['user'].get(obj['closed_by_id'], None)
    #     obj['commodity'] = obj.get('commodity', None)
    #     obj['cargo_readiness_date'] = obj.get('cargo_readiness_date', None)
    #     obj['closing_remarks'] = obj.get('closing_remarks', None)
    #     obj['spot_search'] = service_objects['spot_search'].get(obj['source_id'], None)
    #     obj['preferred_freight_rate'] = obj.get('preferred_rate', None)
    #     obj['preferred_freight_rate_currency'] = obj.get('preferred_rate_currency', None)


# def get_pagination_data(query, page, page_limit):
#     total_count = query.count()
#     total_pages = (total_count + page_limit - 1) // page_limit
#     return {
#         'page': page,
#         'total': total_pages,
#         'total_count': total_count,
#         'page_limit': page_limit
#     }

def get_stats(filters, is_stats_required, performed_by_id):
    if not is_stats_required:
        return {}
    query = FclCfsRateRequest.select()
    if filters:
        if 'status' in filters:
            del filters['status']
        query = apply_direct_filters(query, filters)
        query = apply_indirect_filters(query, filters)
    total_closed_by_user = get_total_closed_by_user(query, performed_by_id)
    total_opened_by_user = get_total_opened_by_user(query, performed_by_id)
    status_count = get_status_count(query)

    total_open = status_count.get('active', 0)
    total_closed = status_count.get('inactive', 0)

    stats = {
        'total': total_open + total_closed,
        'total_closed_by_user': total_closed_by_user,
        'total_opened_by_user': total_opened_by_user,
        'total_open': total_open,
        'total_closed': total_closed
    }
    return {'stats': stats}

def get_total(query):
    return query.count()

def get_total_closed_by_user(query, performed_by_id):
    return query.where(
        (FclCfsRateRequest.status == 'inactive') &
        (FclCfsRateRequest.closed_by_id == performed_by_id)
    ).count()

def get_total_opened_by_user(query, performed_by_id):
    return query.where(
        (FclCfsRateRequest.status == 'active') &
        (FclCfsRateRequest.performed_by_id == performed_by_id)
    ).count()

def get_status_count(query):
    result = query.group_by(FclCfsRateRequest.id, FclCfsRateRequest.status).select(
        FclCfsRateRequest.status,fn.COUNT(FclCfsRateRequest.id).alias('count'))
    status_count = {}
    for row in result:
        status_count[row.status] = row.count

    return status_count