from services.air_freight_rate.models.air_freight_rate_surcharge import AirFreightRateSurcharge
from fastapi import HTTPException


def get_air_freight_rate_surcharge(request):
    details = {}

    if all_fields_present(request):
        object = find_object(request)
        if object:
          details = object.detail()
    else:
      return {}

    if not object:
      object = AirFreightRateSurcharge()
      for key in list(request.keys()):
        setattr(object, key, request[key])
    return details | ({'surcharge_charge_codes': object.possible_charge_codes()})

def all_fields_present(request):
    if request.get('origin_airport_id') and request.get('destination_airport_id') and request.get('operation_type') and request.get('commodity') and request.get('airline_id') and request.get('operation_type') and request.get('service_provider_id'):
        return True
    return False

def find_object(request):
    
    try:
        object = AirFreightRateSurcharge.select().where(AirFreightRateSurcharge.origin_airport_id==request['origin_airport_id'],
                                                         AirFreightRateSurcharge.destination_airport_id==request.get('destination_airport_id'),
                                                         AirFreightRateSurcharge.commodity==request.get('commodity'),
                                                         AirFreightRateSurcharge.airline_id==request.get('airline_id'),
                                                         AirFreightRateSurcharge.operation_type==request.get('operation_type'),
                                                         AirFreightRateSurcharge.service_provider_id==request.get('service_provider_id'),
                                                         ~(AirFreightRateSurcharge.rate_not_available_entry)).first()

    except:
        raise HTTPException(status_code=400, detail="no surcharge entry with the given id exists")
    return object
