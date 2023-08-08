from libs.json_encoder import json_encoder
from math import ceil
from services.air_freight_rate.models.air_freight_warehouse_rate import AirFreightWarehouseRates
from services.fcl_freight_rate.helpers.direct_filters import apply_direct_filters  # we can create helpers for air of=r move fcl helpers to common

POSSIBLE_DIRECT_FILTERS = ['airport_id', 'country_id', 'trade_id', 'continent_id', 'commodity', 'trade_type', 'service_provider_id', 'is_line_items_info_messages_present', 'is_line_items_error_messages_present']

POSSIBLE_INDIRECT_FILTERS = ['location_ids']

def list_air_freight_warehouse_rates(filters={},page=1,page_limit=10):

    filters = {k for k,v  in filters.items() if v is not None}
    unexpected_filters = set(filters.keys()) - (set(POSSIBLE_DIRECT_FILTERS) | set(POSSIBLE_INDIRECT_FILTERS))
    filters = {k for k in filters.items() if k not in unexpected_filters}

    query=get_query()
    query = apply_direct_filters(query,filters,POSSIBLE_DIRECT_FILTERS,AirFreightWarehouseRates)
    query = apply_indirect_filters(query,filters)
    data=get_data(query)
    pagination_data=get_pagination_data(query)
    
    return {'list': json_encoder(data) } | (pagination_data) 


def get_query():
    query=AirFreightWarehouseRates.select().order_by(AirFreightWarehouseRates.priority_score.desc())
    return query

def apply_indirect_filters(query,filters):
    for key in filters:
        if key in POSSIBLE_INDIRECT_FILTERS:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query

def apply_location_ids_filter(query,filters):
    qeury=query.where(AirFreightWarehouseRates.location_ids.contains(filters['location_ids']))
    return query

def get_data(query):
    query=query.select(
        AirFreightWarehouseRates.id,
        AirFreightWarehouseRates.airport_id,
        AirFreightWarehouseRates.trade_type,
        AirFreightWarehouseRates.commodity,
        AirFreightWarehouseRates.line_items,
        AirFreightWarehouseRates.line_items_info_messages,
        AirFreightWarehouseRates.is_line_items_info_messages_present,
        AirFreightWarehouseRates.line_items_error_messages,
        AirFreightWarehouseRates.is_line_items_error_messages_present,
        AirFreightWarehouseRates.airport
    )
    data = list(query.dicts())
    return data

def get_pagination_data(query,page,page_limit):
    total_count = query.count()
  
    pagination_data = {
    'page': page,
    'total': ceil(total_count/page_limit),
    'total_count': total_count,
    'page_limit': page_limit
    }
    return pagination_data