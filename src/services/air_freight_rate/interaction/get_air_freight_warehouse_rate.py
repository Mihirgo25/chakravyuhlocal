from fastapi import HTTPException
from datetime import datetime
from services.air_freight_rate.models.air_freight_warehouse_rate import AirFreightWarehouseRates

def get_air_freight_wareohouse_data(request):
    details={}

    if all_fields_present(request):
        object=find_object(request)
     
        if object:
            details=object.detail()
    else:
        object=None

    if not object:
        object=AirFreightWarehouseRates()
        for key in list(request.keys()):
            setattr(object,key,request[key])
        return details | ({'warehouse_charge_codes':object.possible_charge_codes()})


def all_fields_present(request):
    if request['airport_id'] and request['trade_type'] and request['commodity'] and request['service_provider_id']:
        return True
    return False

def find_object(request):
    try:

        object=AirFreightWarehouseRates.select().where(
            AirFreightWarehouseRates.airport_id==request['airport_id'],
            AirFreightWarehouseRates.trade_type==request['trade_type'],
            AirFreightWarehouseRates.commodity==request['commodity'],
            AirFreightWarehouseRates.service_provider_id==request['service_provider_id']
            ).first()
    except:
        raise HTTPException(status_code=400,detail='no id found')
    return object
