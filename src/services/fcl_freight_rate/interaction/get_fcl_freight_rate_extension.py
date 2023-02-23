from services.fcl_freight_rate.helpers.fcl_freight_rate_cluster_helpers import *


def get_fcl_freight_rate_extension_data(request):
    request = request.__dict__
    row = {
        'service_provider_id' : request['service_provider_id'],
        'shipping_line_id' : request['shipping_line_id'],
        'origin_port_id' : request['origin_port_id'],
        'destination_port_id' : request['destination_port_id'],
        'commodity' : request['commodity'],
        'container_size' : request['container_size'],
        'container_type' : request['container_type']
    }
    cluster_objects = get_cluster_objects(row)

    if not cluster_objects:
        return

    required_mandatory_codes = get_required_mandatory_codes(cluster_objects)
    cluster_objects.last[required_mandatory_codes] = required_mandatory_codes
    return cluster_objects
