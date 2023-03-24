from services.fcl_freight_rate.models.fcl_freight_rate_commodity_surcharge import FclFreightRateCommoditySurcharge
from services.fcl_freight_rate.helpers.find_or_initialize import apply_direct_filters
from math import ceil
from playhouse.shortcuts import model_to_dict
import concurrent.futures, json
possible_direct_filters = ['origin_port_id', 'origin_country_id', 'origin_trade_id', 'origin_continent_id', 'destination_port_id', 'destination_country_id', 'destination_trade_id', 'destination_continent_id', 'shipping_line_id', 'service_provider_id', 'container_size', 'container_type', 'commodity', 'origin_location_id', 'destination_location_id']
possible_indirect_filters = []

def list_fcl_freight_rate_commodity_surcharges(filters = {}, page_limit =10, page = 1, pagination_data_required = True):
    query = get_query(page, page_limit)

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        query = apply_direct_filters(query, filters, possible_direct_filters, FclFreightRateCommoditySurcharge)
        query = apply_indirect_filters(query, filters)
    # with concurrent.futures.ThreadPoolExecutor(max_workers = 2) as executor:
    #     futures = [executor.submit(eval(method_name), query, page, page_limit, pagination_data_required) for method_name in ['get_data', 'get_pagination_data']]
    #     results = {}
    #     for future in futures:
    #         result = future.result()
    #         results.update(result)

    # data = results['get_data']
    # pagination_data = results['get_pagination_data']
    data = get_data(query)['get_data']
    pagination_data = get_pagination_data(data,page, page_limit, pagination_data_required)
    return { 'list': data } | (pagination_data)

def get_query(page, page_limit):
    query = FclFreightRateCommoditySurcharge.select().order_by(FclFreightRateCommoditySurcharge.updated_at.desc()).paginate(page, page_limit)
    return query

def get_data(query):
    query = query.select(
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

    )
    data = list(query.dicts())
    return {'get_data' : data}


def get_pagination_data(data, page, page_limit, pagination_data_required):
    if not pagination_data_required:
        return {'get_pagination_data': {}}
    
    params = {
      'page': page,
      'total': ceil(len(data)/page_limit),
      'total_count': len(data),
      'page_limit': page_limit
    }
    return {'get_pagination_data': params}

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query