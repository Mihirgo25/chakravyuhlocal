from services.fcl_freight_rate.models.fcl_weight_slabs_configuration import FclWeightSlabsConfiguration
from services.fcl_freight_rate.helpers.direct_filters import apply_direct_filters
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from micro_services.client import maps
from playhouse.shortcuts import model_to_dict
from math import ceil
import json

possible_direct_filters = ['origin_location_id', 'destination_location_id', 'origin_location_type', 'destination_location_type', 'oraganization_category', 'shipping_line_id', 'service_provider_id', 'importer_exporter_id', 'is_cogo_assured', 'container_size', 'commodity', 'max_weight', 'trade_type']

def list_fcl_weight_slabs_configuration(filters = {}, page_limit = 10, page = 1, pagination_data_required = True):
    query = get_query(page, page_limit)
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)
    
        query = apply_direct_filters(query, filters, possible_direct_filters, FclWeightSlabsConfiguration)

    data = get_data(query)
    location_ids = []
    for row in data:
        location_ids.extend([str(row['origin_location_id']), str(row['destination_location_id'])])

    locations = maps.list_locations({'filters': {'id': list(set(filter(None, location_ids)))}, 'page_limit' : MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT})
    if locations:
        locations = locations['list']
    else:
        locations = []
        
    locations_hash = {}
    for location in locations:
        locations_hash[str(location['id'])] = location['name']
    
    for i in range(len(data)):
        if data[i]['origin_location_id']:
            data[i]['origin_location_name'] = locations_hash[str(data[i]['origin_location_id'])]
    
        if data[i]['destination_location_id']:
            data[i]['destination_location_name'] = locations_hash[str(data[i]['destination_location_id'])]


    pagination_data = get_pagination_data(data, page, page_limit, pagination_data_required)

    return { 'list': data } | (pagination_data)


def get_query(page, page_limit):
    query = FclWeightSlabsConfiguration.select().where(FclWeightSlabsConfiguration.status == 'active').order_by(FclWeightSlabsConfiguration.updated_at.desc()).paginate(page, page_limit)
    return query

def get_data(query):
    data = list(query.dicts())
    # data = [model_to_dict(item) for item in query.execute()]
    return data

def get_pagination_data(data, page, page_limit, pagination_data_required):
    if not pagination_data_required:
        return {}

    params = {
      'page': page,
      'total': ceil(len(data)/page_limit),
      'total_count': len(data),
      'page_limit': page_limit
    }
    return params