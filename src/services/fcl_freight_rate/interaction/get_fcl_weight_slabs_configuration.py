from services.fcl_freight_rate.models.fcl_weight_slabs_configuration import FclWeightSlabsConfiguration
from playhouse.shortcuts import model_to_dict
import json
from operator import attrgetter
from configs.fcl_freight_rate_constants import LOCATION_HIERARCHY_FOR_WEIGHT 

possible_direct_filters = ['origin_location_id', 'destination_location_id', 'origin_location_type', 'destination_location_type', 'organization_category', 'shipping_line_id', 'service_provider_id', 'importer_exporter_id', 'is_cogo_assured', 'container_size', 'commodity', 'trade_type']

def get_fcl_weight_slabs_configuration(filters = {}):
    query = FclWeightSlabsConfiguration.select().where(FclWeightSlabsConfiguration.status == 'active')

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        direct_filters = {key:value for key,value in filters.items() if key in possible_direct_filters}

        if direct_filters.get('origin_location_id'):
            direct_filters['origin_location_id'].append(None)

        if direct_filters.get('destination_location_id'):
            direct_filters['destination_location_id'].append(None)
        
        if direct_filters.get('origin_location_type'):
            direct_filters['origin_location_type'].append(None)

        if direct_filters.get('destination_location_type'):
            direct_filters['destination_location_type'].append(None)
        
        if direct_filters.get('organization_category'):
            direct_filters['organization_category'].append(None) 
        
        if direct_filters.get('shipping_line_id'):
            direct_filters['shipping_line_id'].append(None) 
        
        if direct_filters.get('service_provider_id'):
            direct_filters['service_provider_id'].append(None)
        
        if direct_filters.get('importer_exporter_id'):
            direct_filters['importer_exporter_id'].append(None) 
        
        if direct_filters.get('container_size'):
            direct_filters['container_size'].append(None) 
        
        if direct_filters.get('commodity'):
            direct_filters['commodity'].append(None) 
        
        if direct_filters.get('is_cogo_assured'):
            direct_filters['is_cogo_assured'].append(None) 
        
        for filter in direct_filters:
            query = query.where(attrgetter(filter)(FclWeightSlabsConfiguration).in_(filters[filter]))
            
    else:
        direct_filters = {}
        
    data = [model_to_dict(item) for item in query.execute()]

    for object in data:
        filters_count = 0
        for key, value in object.items():
            if key in direct_filters:
                if value and direct_filters[key]:
                    filters_count += 1 
        object['filters_count'] = filters_count

    data = sorted(data, key=lambda t: (
        -t['filters_count'],
        0 if t['service_provider_id'] else 1,
        0 if t['organization_category'] else 1,
        0 if t['importer_exporter_id'] else 1,
        0 if t['trade_type'] else 1,
        LOCATION_HIERARCHY_FOR_WEIGHT[t['origin_location_type']] if t['origin_location_type'] else 1,
        LOCATION_HIERARCHY_FOR_WEIGHT[t['destination_location_type']] if t['destination_location_type'] else 1,
        0 if t['shipping_line_id'] else 1,
        0 if t['container_size'] else 1,
        0 if t['commodity'] else 1)
    )

    try:
        return {'max_weight': data[0]['max_weight'], 'slabs':data[0]['slabs']}
    except:
        return None