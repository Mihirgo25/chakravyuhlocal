from services.fcl_freight_rate.models.fcl_freight_rate_weight_limit import FclFreightRateWeightLimit
from playhouse.shortcuts import model_to_dict
from fastapi import HTTPException


def get_fcl_freight_rate_weight_limit(request):
    if not all_fields_present(request):
        return {}
    
    object = find_object(request)
    object = model_to_dict(object)

    if object is None:
        return {}
    return object

def all_fields_present(request):
    for field in (
        'origin_location_id',
        'destination_location_id',
        'container_size',
        'container_type',
        'shipping_line_id',
        'service_provider_id'
    ):
        if field not in request:
            return False
    return True

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
        object = FclFreightRateWeightLimit.get(**row)
    except:
        raise HTTPException(status_code=499, detail="no weight limit entry with the given id exists")
    return object



