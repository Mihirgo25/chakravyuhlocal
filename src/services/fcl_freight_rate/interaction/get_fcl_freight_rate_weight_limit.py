from services.fcl_freight_rate.models.fcl_freight_rate_weight_limit import FclFreightRateWeightLimit
from fastapi import HTTPException

def get_fcl_freight_rate_weight_limit(request):
    if not all_fields_present(request):
        return {}
    
    objects = find_object(request)

    if not objects:
        return {}

    objects = objects.detail()
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
        # objects = FclFreightRateWeightLimit.get(**row)
        objects = FclFreightRateWeightLimit.select().where(
            FclFreightRateWeightLimit.origin_location_id == request['origin_location_id'],
            FclFreightRateWeightLimit.destination_location_id == request['destination_location_id'],
            FclFreightRateWeightLimit.container_type == request['container_type'],
            FclFreightRateWeightLimit.container_size == request['container_size'],
            FclFreightRateWeightLimit.shipping_line_id == request['shipping_line_id'],
            FclFreightRateWeightLimit.service_provider_id == request['service_provider_id']
        ).first()

    except:
        raise HTTPException(status_code=400, detail="no weight limit entry with the given id exists")
    return objects