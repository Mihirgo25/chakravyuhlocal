from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
from fastapi import HTTPException

def get_air_freight_rate_local(request):
    details={}
    if all_fields_present(request):
        object = find_object(request)
        print(112)
        if object:
          details = object.detail()
         

    else:
      object=None

    
    if not object:
        object=AirFreightRateLocal()
        for key in list(request.keys()):
            setattr(object,key,request[key])
    # return details | ({'local_charge_codes':object.possible_charge_codes()})
    return details


def all_fields_present(request):
    # if((object_params['airport_id'] is not None) and (object_params['airline_id'] is not None) and (object_params['trade_type'] is not None) and (object_params['commodity'] is not None) and (object_params['service_provider_id'] is not None)):
    #     return True
    # return False
    if request.get('airport_id') and request.get('airline_id') and request.get('trade_type') and request.get('commodity') and request.get('service_provider_id'):
        return True
    return False
    
def find_object(request):
    # object = AirFreightRateLocal.select().where(
    # AirFreightRateLocal.airport_id == request.get("airport_id"),
    # AirFreightRateLocal.airline_id == request.get("airline_id"),
    # AirFreightRateLocal.trade_type == request.get("trade_type"),
    # AirFreightRateLocal.commodity == request.get("commodity"),
    # AirFreightRateLocal.service_provider_id == request.get('service_provider_id'),
    # ).first()

    row = {
        'airport_id' : request.get("airport_id"),
        'airline_id' : request.get("airline_id"),
        'trade_type' : request.get("trade_type"),
        'commodity': request.get("commodity"),
        'service_provider_id':request.get('service_provider_id')
        }
    
    try:
        objects = AirFreightRateLocal.get(**row)
    
    except:
        raise HTTPException(status_code=400, detail="no local rates entry with the given id exists")

    return objects

    
def get_object_params(request):
    return request