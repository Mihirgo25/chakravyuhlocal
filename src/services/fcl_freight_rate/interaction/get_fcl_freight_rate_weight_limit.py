from services.fcl_freight_rate.models.fcl_freight_rate_weight_limit import FclFreightRateWeightLimit
from playhouse.shortcuts import model_to_dict
from fastapi import HTTPException


def get_fcl_freight_rate_weight_limit(request):
    if not all_fields_present(request):
        return {}
    
    objects = find_object(request)
    objects = model_to_dict(objects)

    if not objects:
        return {}
    return objects

def all_fields_present(request):
    if request['origin_location_id'] and request['destination_location_id'] and request['container_size'] and request['container_type'] and request['shipping_line_id'] and request['service_provider_id']:
        return True
    return False

def find_object(request):
    row = {
        'origin_location_id' : request['origin_location_id'],
        'destination_location_id' : request['destination_location_id'],
        'container_type' : request['container_type'],
        'container_size' : request['container_size'],
        'shipping_line_id' : request['shipping_line_id'],
        'service_provider_id' : request['service_provider_id']
    }

    try:
        objects = FclFreightRateWeightLimit.get(**row)
    except:
        raise HTTPException(status_code=403, detail="no weight limit entry with the given id exists")
    return objects