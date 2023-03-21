from services.fcl_freight_rate.models.fcl_freight_rate_commodity_surcharge import FclFreightRateCommoditySurcharge
from fastapi import HTTPException


def get_fcl_freight_rate_commodity_surcharge(request):
    if not all_fields_present(request):
        return {}

    objects = find_object(request)
    
    if not objects:
        return {}
    
    objects = objects.detail()
    return objects

def all_fields_present(request):
    if request.get('origin_location_id') and request.get('destination_location_id') and request.get('container_size') and request.get('container_type') and request.get('commodity') and request.get('shipping_line_id') and request.get('service_provider_id'):
        return True
    return False

def find_object(request):
    row = {
        'origin_location_id' : request['origin_location_id'],
        'destination_location_id' : request['destination_location_id'],
        'container_type' : request['container_type'],
        'container_size' : request['container_size'],
        'commodity' : request['commodity'],
        'shipping_line_id' : request['shipping_line_id'],
        'service_provider_id' : request['service_provider_id']
    }
    
    try:
        objects = FclFreightRateCommoditySurcharge.get(**row)
    except:
        raise HTTPException(status_code=403, detail="no commodity surcharge entry with the given id exists")
    return objects