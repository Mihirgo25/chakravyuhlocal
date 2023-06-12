from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
from fastapi import HTTPException

def get_air_freight_rate_local(request):
    details={}
    if all_fields_present(request):
        object = AirFreightRateLocal.select().where(
            AirFreightRateLocal.airport_id == request.get('airport_id'),
            AirFreightRateLocal.airline_id == request.get('airline_id'),
            AirFreightRateLocal.trade_type == request.get('trade_type'),
            AirFreightRateLocal.commodity == request.get('commodity'),
            AirFreightRateLocal.service_provider_id == request.get('service_provider_id')
        ).first()
        if object:
          details = object.detail()
    else:
      return {}

    if not object:
        object=AirFreightRateLocal()
        for key in list(request.keys()):
            setattr(object,key,request[key])
    return details | ({'local_charge_codes':object.possible_charge_codes()})


def all_fields_present(request):
    if request.get('airport_id') and request.get('airline_id') and request.get('trade_type') and request.get('commodity') and request.get('service_provider_id'):
        return True
    return False
    

def get_object_params(request):
    return request