
from rails_client import client
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from libs.locations import list_locations,list_location_clusters
from services.fcl_freight_rate.interaction.list_fcl_freight_commodity_clusters import list_fcl_freight_commodity_clusters
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_local_agents import list_fcl_freight_rate_local_agents
def get_multiple_service_objects(freight_object,service_objects):
    client.initialize_client()
    data = client.ruby.get_multiple_service_objects_data_for_fcl(service_objects)
    freight_object.object_data = data
    freight_object.save()

    return data
        
