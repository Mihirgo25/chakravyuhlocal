from services.fcl_freight_rate.models.fcl_freight_rate_seasonal_surcharge import FclFreightRateSeasonalSurcharge
from configs.defintions import FCL_FREIGHT_SEASONAL_CHARGES
from fastapi import HTTPException


def get_fcl_freight_rate_seasonal_surcharge(request):
    fcl_freight_seasonal_charges = FCL_FREIGHT_SEASONAL_CHARGES
    
    if not all_fields_present(request):
        return {'seasonal_surcharge_charge_codes': fcl_freight_seasonal_charges} 

    try:
        detail = find_object(request).detail()
    except:
        detail = {}

    return detail | {'seasonal_surcharge_charge_codes': fcl_freight_seasonal_charges}


def all_fields_present(request):
    if request.get('origin_location_id') and request.get('destination_location_id') and request.get('container_size') and request.get('container_type') and request.get('code') and request.get('shipping_line_id') and request.get('service_provider_id'):
        return True
    else:
        return False

def find_object(request):
    row = {
        'origin_location_id' : request['origin_location_id'],
        'destination_location_id' : request['destination_location_id'],
        'code' : request['code'],
        'container_type' : request['container_type'],
        'container_size' : request['container_size'],
        'shipping_line_id' : request['shipping_line_id'],
        'service_provider_id' : request['service_provider_id']
    }
    
    try:
        objects = FclFreightRateSeasonalSurcharge.get(**row)
    except:
        raise HTTPException(status_code=403, detail="no seasonal surcharge entry with the given id exists")
    return objects