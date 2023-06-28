from services.air_freight_rate.models.air_freight_location_clusters import AirFreightLocationClusters
from services.air_freight_rate.models.air_freight_location_cluster_mapping import AirFreightLocationClusterMapping
from services.air_freight_rate.models.air_freight_location_cluster_factor import AirFreightLocationClusterFactor
from fastapi.encoders import jsonable_encoder
from database.db_session import db


def create_cluster_factor_mapping():
    cluster_data = AirFreightLocationClusters.select(AirFreightLocationClusters.id).execute()
    data_list = [row.id for row in cluster_data]
    location_data=AirFreightLocationClusterMapping.select(AirFreightLocationClusterMapping.location_id,AirFreightLocationClusterMapping.cluster_id)
    location_data = jsonable_encoder(list(location_data.dicts()))
    cluster_wise_locs = {}
    for loc in location_data:
        if loc['cluster_id'] in cluster_wise_locs:
            values = cluster_wise_locs[loc['cluster_id']] or []
            values.append(loc['location_id'])
            cluster_wise_locs[loc['cluster_id']] = values
        else:
            cluster_wise_locs[loc['cluster_id']] = [loc['location_id']]
    
    print(len(location_data), len(cluster_wise_locs.keys()))
    
    
    for origin_cluster_id in data_list:
        for destination_cluster_id in data_list:
            if origin_cluster_id == destination_cluster_id:
                continue
            factor_list = []
            origin_locs = cluster_wise_locs[origin_cluster_id]
            destination_locs = cluster_wise_locs[destination_cluster_id]
            for origin_loc in origin_locs:
                object = {
                    'cluster_id': origin_cluster_id,
                    'origin_cluster_id': origin_cluster_id,
                    'destination_cluster_id': destination_cluster_id,
                    'location_id': origin_loc
                }
                factor_list.append(object)
            for destination_loc in destination_locs:
                object = {
                    'cluster_id': destination_cluster_id,
                    'origin_cluster_id': origin_cluster_id,
                    'destination_cluster_id': destination_cluster_id,
                    'location_id': destination_loc
                }
                factor_list.append(object)
            AirFreightLocationClusterFactor.insert_many(factor_list).execute()