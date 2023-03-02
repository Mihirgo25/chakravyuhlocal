from services.fcl_freight_rate.models.fcl_weight_slabs_configuration import FclWeightSlabsConfiguration
from services.fcl_freight_rate.interaction.list_fcl_freight_rates import remove_unexpected_filters
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from operator import attrgetter
from rails_client import client
from playhouse.shortcuts import model_to_dict
from math import ceil

possible_direct_filters = ['origin_location_id', 'destination_location_id', 'origin_location_type', 'destination_location_type', 'oraganization_category', 'shipping_line_id', 'service_provider_id', 'importer_exporter_id', 'is_cogo_assured', 'container_size', 'commodity', 'max_weight', 'trade_type']

def list_fcl_weight_slabs_configuration(filters, page, page_limit):
    filters = remove_unexpected_filters(filters)
    query = get_query(page, page_limit)
    query = apply_direct_filters(query, filters)
    data = get_data(query)
    locations = client.ruby.list_locations({'filters': {'id': list(set(filter(None, [row['origin_location_id'] for row in data] + [row['destination_location_id'] for row in data])))}, 'page_limit':MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT})['list']
    locations_hash = {}
    for location in locations:
        locations_hash[str(location['id'])] = location['name']
    
    new_data = []
    for object in data:
        if object['origin_location_id']:
            object['origin_location_name'] = locations_hash[object['origin_location_id']]
    
        if object['destination_location_id']:
            object['destination_location_name'] = locations_hash[object['destination_location_id']]
        new_data.append(object)

    pagination_data = get_pagination_data(query)
    return { 'list': new_data } | (pagination_data)


def get_query(page, page_limit):
    query = FclWeightSlabsConfiguration.select().where(FclWeightSlabsConfiguration.status == 'active').order_by(FclWeightSlabsConfiguration.updated_at.desc()).paginate(page, page_limit)
    return query

def apply_direct_filters(query, filters):  
    for key in filters:
        if key in possible_direct_filters:
            query = query.select().where(attrgetter(key)(FclWeightSlabsConfiguration) == filters[key])
    return query

def get_data(query):
    data = [model_to_dict(item) for item in query.execute()]
    return data

def get_pagination_data(query, page, page_limit, pagination_data_required):
    if not pagination_data_required:
        return {}

    params = {
      'page': page,
      'total': ceil(query.count()/page_limit),
      'total_count': query.count(),
      'page_limit': page_limit
    }
    return params
