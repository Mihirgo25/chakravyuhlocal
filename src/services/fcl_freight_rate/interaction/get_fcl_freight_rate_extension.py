from services.fcl_freight_rate.helpers.fcl_freight_rate_cluster_helpers import *

def get_fcl_freight_rate_extension_data(request):
    request = request.__dict__
    cluster_objects = get_cluster_objects(request)
    cluster_objects = [(value | {'cluster_type':key}) for key,value in cluster_objects.items()]
    if not cluster_objects:
        return

    required_mandatory_codes = get_required_mandatory_codes(cluster_objects)
    cluster_objects[-1]['required_mandatory_codes'] = required_mandatory_codes
    return cluster_objects
