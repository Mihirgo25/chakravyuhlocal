from services.fcl_freight_rate.models.fcl_freight_location_cluster import FclFreightLocationCluster
from services.fcl_freight_rate.models.fcl_freight_location_cluster_mapping import FclFreightLocationClusterMapping
from database.db_session import db

def create_fcl_freight_location_cluster(request):
    with db.atomic():
        cluster_params = {
            'base_port_id':request.get('base_port_id'),
            'map_zone_id':request.get('map_zone_id'),
            'status':'active'
        }
        cluster = FclFreightLocationCluster.create(**cluster_params)
        cluster_id = cluster.id

        cluster_mappings = []
        for location_id in request.get('location_ids'):
            row = {
                'location_id':location_id,
                'cluster_id':cluster_id
            }
            cluster_mappings.append(row)
        
        FclFreightLocationClusterMapping.insert_many(cluster_mappings).execute()