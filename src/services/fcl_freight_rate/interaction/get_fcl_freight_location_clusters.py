from services.fcl_freight_rate.models.fcl_freight_location_cluster import FclFreightLocationCluster
from services.fcl_freight_rate.models.fcl_freight_location_cluster_mapping import FclFreightLocationClusterMapping
from services.fcl_freight_rate.models.fcl_freight_location_cluster_factor import FclFreightLocationClusterFactor
from fastapi.encoders import jsonable_encoder

def get_factors(origin_cluster_id, destination_cluster_id, cluster_ids, container_size, container_type, shipping_line_id):
    query = FclFreightLocationClusterFactor.select(
        FclFreightLocationClusterFactor.rate_factor,
        FclFreightLocationClusterFactor.cluster_id,
        FclFreightLocationClusterFactor.location_id
    ).where(
        FclFreightLocationClusterFactor.cluster_id << cluster_ids,
        FclFreightLocationClusterFactor.status == 'active',
        FclFreightLocationClusterFactor.origin_cluster_id == origin_cluster_id,
        FclFreightLocationClusterFactor.destination_cluster_id == destination_cluster_id,
        (FclFreightLocationClusterFactor.container_size.is_null(True) | FclFreightLocationClusterFactor.container_size == container_size),
        (FclFreightLocationClusterFactor.container_type.is_null(True) | FclFreightLocationClusterFactor.container_type == container_type),
        (FclFreightLocationClusterFactor.shipping_line_id.is_null(True) | FclFreightLocationClusterFactor.shipping_line_id == shipping_line_id)
    )
    
    return jsonable_encoder(list(query.dicts()))

def get_rate_param(rate, origin_port_id, destination_port_id, factor=1):
    new_rate = rate.copy()
    new_rate['origin_port_id'] = origin_port_id
    new_rate['destination_port_id'] = destination_port_id
    for item in new_rate['line_items']:
        if item['code'] == 'BAS':
            item['price'] == item['price'] * factor
            
    return new_rate

def get_cluster_rate_combinations(rate):
    origin_port_id = rate['origin_port_id']
    destination_port_id = rate['destination_port_id']
    container_size = rate['container_size']
    container_type = rate['container_type']
    shipping_line_id = rate['shipping_line_id']
    
    clusters_query = FclFreightLocationCluster.select(
        FclFreightLocationCluster.id,
        FclFreightLocationCluster.base_port_id
    ).where(
        FclFreightLocationCluster.base_port_id in [origin_port_id, destination_port_id],
        FclFreightLocationCluster.status == 'active'
    )
    
    clusters = jsonable_encoder(list(clusters_query.dicts()))
    
    origin_cluster_id = None
    destination_cluster_id = None
    
    for cluster in clusters:
        if cluster['base_port_id'] == origin_port_id:
            origin_cluster_id = cluster['id']
        if cluster['base_port_id'] == destination_port_id:
            destination_cluster_id = cluster['id']
            
    cluster_ids = []
    if origin_cluster_id:
        cluster_ids.append(origin_cluster_id)
        
    if destination_cluster_id:
        cluster_ids.append(destination_cluster_id)
        
    all_rates = []
    if cluster_ids:
        location_cluster_ids = []
        if not origin_cluster_id:
            cluster = FclFreightLocationClusterMapping.select(FclFreightLocationClusterMapping.cluster_id).where(FclFreightLocationClusterMapping.location_id == origin_port_id).first()
            origin_cluster_id = cluster.cluster_id
        else:
            location_cluster_ids.append(origin_cluster_id)
            
        if not destination_cluster_id:
            cluster = FclFreightLocationClusterMapping.select(FclFreightLocationClusterMapping.cluster_id).where(FclFreightLocationClusterMapping.location_id == destination_port_id).first()
            destination_cluster_id = cluster.cluster_id
        else:
            location_cluster_ids.append(destination_cluster_id)
            
    factor_mappings = get_factors(origin_cluster_id, destination_cluster_id, location_cluster_ids, container_size, container_type, shipping_line_id)
    
    for factor_mapping in factor_mappings:
        if factor_mapping['cluster_id'] == origin_cluster_id:
            rate_params = get_rate_param(rate, factor_mapping['location_id'], destination_port_id, factor_mapping['rate_factor'])
            
        if factor_mapping['cluster_id'] == destination_cluster_id:
            rate_params = get_rate_param(rate, origin_port_id, factor_mapping['location_id'], factor_mapping['rate_factor'])
        
        all_rates.append(rate_params)
        
    return all_rates
            