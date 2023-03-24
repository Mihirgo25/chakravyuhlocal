from services.fcl_freight_rate.helpers.fcl_freight_rate_cluster_helpers import *

def get_fcl_freight_rate_extension_data(service_provider_id, shipping_line_id, origin_port_id, destination_port_id, commodity, container_size, container_type):
    row = {
        'service_provider_id': service_provider_id, 
        'shipping_line_id': shipping_line_id, 
        'origin_port_id': origin_port_id, 
        'destination_port_id': destination_port_id, 
        'commodity': commodity, 
        'container_size': container_size, 
        'container_type': container_type
    }

    cluster_objects = get_cluster_objects(row)
    cluster_objects = [(value | {'cluster_type':key}) for key,value in cluster_objects.items()]
    if not cluster_objects:
        return

    required_mandatory_codes = get_required_mandatory_codes(cluster_objects)
    cluster_objects[-1]['required_mandatory_codes'] = required_mandatory_codes
    return cluster_objects
