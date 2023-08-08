
from services.air_freight_rate.models.air_freight_location_cluster import AirFreightLocationCluster
from services.air_freight_rate.models.air_freight_location_cluster_mapping import AirFreightLocationClusterMapping
from database.db_session import db

def create_clusters(request):
    with db.atomic():
        cluster_params = {
            'base_airport_id':request.get('base_airport_id'),
            'map_zone_id':request.get('map_zone_id'),
            'status':'active'
        }
        cluster = AirFreightLocationCluster.create(**cluster_params)
        cluster_id = cluster.id

        cluster_mappings = []
        for location in request.get('location_ids'):
            row = {
                'location_id':location,
                'cluster_id':cluster_id
            }
            cluster_mappings.append(row)
        
        AirFreightLocationClusterMapping.insert_many(cluster_mappings).execute()
