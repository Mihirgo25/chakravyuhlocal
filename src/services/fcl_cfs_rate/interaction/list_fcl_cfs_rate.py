from typing import List, Dict
from peewee import *
from fcl_cfs_rate.models.fcl_cfs_rate import FclCfsRate
POSSIBLE_DIRECT_FILTERS = ['id', 'location_id', 'country_code', 'trade_id', 'content_id', 'trade_type', 'service_provider id', 'importer_exporter_id', 'commodity', 'container_type', 'container_size', 'cargo_handling_type']
POSSIBLE_INDIRECT_FILTERS = ['location_ids', 'importer_exporter_present', 'is_rate_available']


def list_fcl_cfs_rate(filters = {}, page_limit = 10, page = 1, sort_by = 'updated_at', sort_type = 'desc', return_query = False,pagination_data_required=True ):
    query = get_query(filters, sort_by, sort_type, page, page_limit)
    query = apply_direct_filters(query, filters)
    query = apply_indirect_filters(query, filters)

    if return_query:
        return {'list': query}

    executors = ['get_data', 'get_pagination_data']
    method_responses = {}

    for method_name in executors:
        method_responses.update({method_name: globals()[method_name](query)})

    data = method_responses['get_data']
    pagination_data = method_responses['get_pagination_data']

    return {'list': data, **pagination_data}

def get_query(filters, sort_by, sort_type, page, page_limit):
    query = FclCfsRate.select().order_by(f"{sort_by} {sort_type}").paginate(page, page_limit)
    return query

def apply_direct_filters(query, filters):
    direct_filters = {k: v for k, v in filters.items() if k in POSSIBLE_DIRECT_FILTERS}
    for k, v in direct_filters.items():
        query = query.where(getattr(FclCfsRate, k) == v)
    return query

def apply_indirect_filters(query, filters):
    indirect_filters = {k: v for k, v in filters.items() if k in POSSIBLE_INDIRECT_FILTERS}
    for filter, value in indirect_filters.items():
        query = getattr(FclCfsRate, f"apply_{filter}_filter")(query, value)
    return query

def apply_location_ids_filter(query, location_ids):
    query = query.where(FclCfsRate.location_ids << location_ids)
    return query

def apply_is_rate_available_filter(query, _):
    query = query.where(FclCfsRate.rate_not_available_entry != 'true')
    return query

def get_data(query):
    fields = [
        FclCfsRate.id,
        FclCfsRate.location_id,
        FclCfsRate.service_provider_id,
        FclCfsRate.trade_type,
        FclCfsRate.importer_exporter_id,
        FclCfsRate.commodity,
        FclCfsRate.container_type,
        FclCfsRate.container_size,
        FclCfsRate.line_items,
        FclCfsRate.free_days,
        FclCfsRate.is_line_items_error_messages_present,
        FclCfsRate.is_line_items_info_messages_present,
        FclCfsRate.line_items_error_messages,
        FclCfsRate.line_items_info_messages,
        FclCfsRate.cargo_handling_type
    ]
    data = query.select(*fields).dicts()

    return list(data)

def get_pagination_data(query):
    return {
        'page': query.paginator.page,
        'total': query.paginator.total_pages,
        'total_count': query.count(),
        'page_limit': query.paginator.per_page
    }