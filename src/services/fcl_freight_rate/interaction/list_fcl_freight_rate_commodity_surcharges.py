from services.fcl_freight_rate.models.fcl_freight_rate_commodity_surcharge import FclFreightRateCommoditySurcharge
from libs.json_encoder import json_encoder
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
from math import ceil
import json

possible_direct_filters = ['origin_port_id', 'origin_country_id', 'origin_trade_id', 'origin_continent_id', 'destination_port_id', 'destination_country_id', 'destination_trade_id', 'destination_continent_id', 'shipping_line_id', 'service_provider_id', 'container_size', 'container_type', 'commodity', 'origin_location_id', 'destination_location_id']
possible_indirect_filters = []

def list_fcl_freight_rate_commodity_surcharges(filters = {}, page_limit =10, page = 1, pagination_data_required = True):
    query = get_query()

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)
        
        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, FclFreightRateCommoditySurcharge)
        query = apply_indirect_filters(query, indirect_filters)

    pagination_data = get_pagination_data(query,page, page_limit, pagination_data_required)
    query = query.paginate(page, page_limit)
    data = json_encoder(list(query.dicts()))

    return { 'list': data } | (pagination_data)

def get_query():
    query = FclFreightRateCommoditySurcharge.select(
            FclFreightRateCommoditySurcharge.id,
            FclFreightRateCommoditySurcharge.origin_location_id,
            FclFreightRateCommoditySurcharge.destination_location_id,
            FclFreightRateCommoditySurcharge.shipping_line_id,
            FclFreightRateCommoditySurcharge.service_provider_id,
            FclFreightRateCommoditySurcharge.container_size,
            FclFreightRateCommoditySurcharge.container_type,
            FclFreightRateCommoditySurcharge.commodity,
            FclFreightRateCommoditySurcharge.price,
            FclFreightRateCommoditySurcharge.currency,
            FclFreightRateCommoditySurcharge.remarks,
            FclFreightRateCommoditySurcharge.shipping_line,
            FclFreightRateCommoditySurcharge.origin_location,
            FclFreightRateCommoditySurcharge.destination_location,
            FclFreightRateCommoditySurcharge.service_provider
    ).order_by(FclFreightRateCommoditySurcharge.updated_at.desc())
    return query

def get_pagination_data(query, page, page_limit, pagination_data_required):
    if not pagination_data_required:
        return {}
        
    total_count = query.count()
    params = {
      'page': page,
      'total': ceil(total_count/page_limit),
      'total_count': total_count,
      'page_limit': page_limit
    }
    return params

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query