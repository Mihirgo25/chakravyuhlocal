from services.fcl_freight_rate.interaction.list_fcl_freight_rates import remove_unexpected_filters
from services.fcl_freight_rate.models.fcl_freight_rate_seasonal_surcharge import FclFreightRateSeasonalSurcharge
from rails_client import client
from operator import attrgetter
from math import ceil
import concurrent.futures

possible_direct_filters = ['origin_port_id', 'origin_country_id', 'origin_trade_id', 'origin_continent_id', 'destination_port_id', 'destination_country_id', 'destination_trade_id', 'destination_continent_id', 'shipping_line_id', 'service_provider_id', 'container_size', 'container_type', 'code', 'origin_location_id', 'destination_location_id']
possible_indirect_filters = []

def list_fcl_freight_rate_seasonal_surcharges(filters, page, page_limit, pagination_data_required):
    filters = remove_unexpected_filters(filters)
    query = get_query(page, page_limit)
    query = apply_direct_filters(query)
    query = apply_indirect_filters(query)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(eval(method_name), query, page, page_limit, pagination_data_required) for method_name in ['get_data', 'get_pagination_data']]
        results = {}
        for future in futures:
            result = future.result()
            results.update(result)
        
    method_responses = results
    data = method_responses['get_data']
    pagination_data = method_responses['get_pagination_data']

    return { 'list': data } | (pagination_data)


def get_query(page, page_limit):
    query = FclFreightRateSeasonalSurcharge.select().order_by(FclFreightRateSeasonalSurcharge.updated_at.desc()).paginate(page, page_limit)
    return query

def get_data(query):
    data = query.select(
            FclFreightRateSeasonalSurcharge.id,
            FclFreightRateSeasonalSurcharge.origin_location_id,
            FclFreightRateSeasonalSurcharge.destination_location_id,
            FclFreightRateSeasonalSurcharge.shipping_line_id,
            FclFreightRateSeasonalSurcharge.service_provider_id,
            FclFreightRateSeasonalSurcharge.container_size,
            FclFreightRateSeasonalSurcharge.container_type,
            FclFreightRateSeasonalSurcharge.validity_start,
            FclFreightRateSeasonalSurcharge.validity_end,
            FclFreightRateSeasonalSurcharge.code,
            FclFreightRateSeasonalSurcharge.price,
            FclFreightRateSeasonalSurcharge.currency,
            FclFreightRateSeasonalSurcharge.remarks
    )

    data = add_service_objects(data)
    return data

def add_service_objects(data):
    service_objects = client.ruby.get_multiple_service_object_data_for_fcl({'objects': [
        {
        'name': 'operator',
        'filters': { 'id': list(set([t['shipping_line_id'] for t in data]))},
        'fields': ['id', 'business_name', 'short_name', 'logo_url']
        },
        {
        'name': 'location',
        'filters': { 'id': {"id": list(set(item for sublist in [[item["origin_location_id"], item["destination_location_id"]] for item in data] for item in sublist))}},
        'fields': ['id', 'name', 'display_name', 'port_code', 'type']
        },
        {
        'name': 'organization',
        'filters': { 'id': list(set([t['servicce_provider_id'] for t in data]))},
        'fields': ['id', 'business_name', 'short_name']
        }
    ]}) 

    for i in range(len(data)):
        data[i]['shipping_line'] = service_objects['operator'][data[i]['shipping_line_id']] if 'operator' in service_objects and data[i].get('shipping_line_id') in service_objects['operator'] else None
        data[i]['origin_location'] = service_objects['location'][data[i]['origin_location_id']] if 'location' in service_objects and data[i].get('origin_location_id') in service_objects['location'] else None
        data[i]['shipping_line'] = service_objects['location'][data[i]['destination_location_id']] if 'location' in service_objects and data[i].get('destination_location_id') in service_objects['location'] else None
        data[i]['service_provider'] = service_objects['organization'][data[i]['service_provider_id']] if 'organization' in service_objects and data[i].get('service_provider_id') in service_objects['organization'] else None
    return data

     
def get_pagination_data(query, pagination_data_required, page, page_limit):
  if not pagination_data_required:
    return {}

  pagination_data = {
    'page': page,
    'total': ceil(query.count()/page_limit),
    'total_count': query.count(),
    'page_limit': page_limit
    }
  
  return pagination_data

def apply_direct_filters(query,filters):
  for key in filters:
    if key in possible_direct_filters:
      query = query.select().where(attrgetter(key)(FclFreightRateSeasonalSurcharge) == filters[key])
  return query

def apply_indirect_filters(query, filters):
  for key in filters:
    if key in possible_indirect_filters:
      apply_filter_function = f'apply_{key}_filter'
      query = eval(f'{apply_filter_function}(query, filters)')
  return query
