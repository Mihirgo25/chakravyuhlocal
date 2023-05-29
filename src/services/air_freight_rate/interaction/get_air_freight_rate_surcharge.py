from services.air_freight_rate.models.air_freight_rate_surcharge import AirFreightRateSurcharge
from fastapi import HTTPException


def get_air_freight_rate_surcharge(request):
    if not all_fields_present(request):
        return {}

    objects = find_object(request)
    
    if not objects:
        return {}
    
    objects = objects.detail()
    return objects.update({'surcharge_charge_codes': AirFreightRateSurcharge(get_object_params()).possible_charge_codes()})

def all_fields_present(request):
    if request.get('origin_airport_id') and request.get('destination_airport_id') and request.get('container_size') and request.get('commodity') and request.get('airline_id') and request.get('operation_type') and request.get('service_provider_id'):
        return True
    return False

def find_object(request):
    row = {
        'origin_airport_id' : request.get("origin_airport_id"),
        'destination_airport_id' : request.get("destination_airport_id"),
        'commodity_type' : request.get("commodity_type"),
        'commodity' : request.get("commodity"),
        'airline_id': request.get("airline_id"),
        'operation_type':request.get('operation_type'),
        'service_provider_id':request.get('service_provider_id')
        }
   
    try:
        objects = AirFreightRateSurcharge.get(**row)
    except:
        raise HTTPException(status_code=400, detail="no surcharge entry with the given id exists")
    return objects
def get_object_params(request):
    return request



