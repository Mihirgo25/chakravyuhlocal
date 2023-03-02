from services.fcl_freight_rate.models.fcl_freight_rate_weight_limit import FclFreightRateWeightLimit
from operator import attrgetter
from math import ceil 
from rails_client import client
import concurrent.futures
from playhouse.shortcuts import model_to_dict
from services.fcl_freight_rate.interaction.list_fcl_freight_rates import remove_unexpected_filters

possible_direct_filters = ['origin_port_id', 'origin_country_id', 'origin_trade_id','origin_continent_id', 'destination_port_id', 'destination_country_id', 'destination_trade_id', 'destination_continent_id', 'shipping_line_id', 'service_provider_id', 'container_size', 'container_type', 'commodity', 'is_slabs_missing']
possible_indirect_filters = []

def list_fcl_freight_rate_weight_limits(filters, page, page_limit, pagination_data_required):
  filters = remove_unexpected_filters(filters, possible_direct_filters, possible_indirect_filters)
  query = get_query(page, page_limit)
  query = apply_direct_filters(query, filters)
  query = apply_indirect_filters(query, filters)

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
    query = FclFreightRateWeightLimit.select().order_by(FclFreightRateWeightLimit.updated_at.desc()).paginate(page, page_limit)
    return query
  
def get_data(query, page, page_limit, pagination_data_required):
  data = query.select(FclFreightRateWeightLimit.id,FclFreightRateWeightLimit.origin_location_id,FclFreightRateWeightLimit.destination_location_id,FclFreightRateWeightLimit.shipping_line_id,FclFreightRateWeightLimit.service_provider_id,FclFreightRateWeightLimit.container_size,FclFreightRateWeightLimit.container_type,FclFreightRateWeightLimit.free_limit,FclFreightRateWeightLimit.remarks,FclFreightRateWeightLimit.slabs,FclFreightRateWeightLimit.is_slabs_missing)
  data = [model_to_dict(item) for item in data.execute()]

  data = add_service_objects(data)
  return {'get_data':data}

def add_service_objects(data):
  service_objects = client.ruby.get_multiple_service_objects_data_for_fcl({'objects': [
    {
      'name': 'operator',
      'filters': { 'id': list(set([str(t['shipping_line_id']) for t in data]))},
      'fields': ['id', 'business_name', 'short_name', 'logo_url']
    },
    {    
      'name': 'location',
      'filters': {'id': list(set(item for sublist in [[str(item["origin_location_id"]), str(item["destination_location_id"])] for item in data] for item in sublist))},
      'fields': ['id', 'name', 'display_name', 'port_code', 'type']
    },
    {
      'name': 'organization',
      'filters': { 'id': list(set([str(t['service_provider_id']) for t in data]))},
      'fields': ['id', 'business_name', 'short_name']
    }
  ]})
  
  new_data = []
  for objects in data:
    objects['shipping_line'] = service_objects['operator'][objects['shipping_line_id']] if 'operator' in service_objects and objects.get('shipping_line_id') in service_objects['operator'] else None
    objects['origin_location']= service_objects['location'][objects['origin_location_id']] if 'location' in service_objects and objects.get('origin_location_id') in service_objects['location'] else None
    objects['destination_location'] = service_objects['location'][objects['destination_location_id']] if 'location' in service_objects and objects.get('destination_location_id') in service_objects['location'] else None
    objects['service_provider'] = service_objects['organization'][objects['service_provider_id']] if 'organization' in service_objects and objects.get('service_provider_id') in service_objects['organization'] else None
    new_data.append(objects)
  return new_data

def get_pagination_data(query, page, page_limit, pagination_data_required):
    if not pagination_data_required:
        return {'get_pagination_data':{}} 

    params = {
      'page': page,
      'total': ceil(query.count()/page_limit),
      'total_count': query.count(),
      'page_limit': page_limit
    }
    return {'get_pagination_data':params}

def apply_direct_filters(query, filters):
    for key in filters:
        if key in possible_direct_filters:
            query = query.select().where(attrgetter(key)(FclFreightRateWeightLimit) == filters[key])
    return query

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query