from configs.definitions import AIR_FREIGHT_CHARGES
from configs.definitions import AIR_FREIGHT_SURCHARGES
from configs.definitions import AIR_FREIGHT_LOCAL_CHARGES
from fastapi import HTTPException
import pdb
def list_air_freight_charge_codes(request):
    validate(request)
    charges = get_charge_codes(request)
    print(charges)
    if not charges:
        return {}
    return charges

def get_charge_codes(request):
    charge_codes = {}
    if request.get('commodity_sub_type') or request.get('commodity_type') or request.get('commodity'):
        return get_possible_charge_codes(request)
    elif request.get('service_type') == 'air_freight_surcharges':
        charge_codes = AIR_FREIGHT_SURCHARGES
    elif request.get('service_type') == 'air_freight':
        charge_codes = AIR_FREIGHT_CHARGES
    else:
        charge_codes = AIR_FREIGHT_LOCAL_CHARGES

    response = {"list": []}
    for code, config in charge_codes.items():
        if "deleted" in config.get("tags", []):
            continue
        if request.get('service_type') == 'air_freight_local' and request.get('trade_type') and request.get('trade_type') not in config.get("trade_types"):
            continue
        response["list"].append({
            "code": code,
            "name": config.get("name"),
            "units": config.get("units"),
            "condition": config.get("condition"),
            "tags": config.get("tags"),
            "trade_types": config.get("trade_types"),
            "sac_code": config.get("sac_code"),
        })

    return response


def get_possible_charge_codes(request):
    
    if request.get('service_type') == 'air_freight_surcharges':
        charge_codes = AIR_FREIGHT_SURCHARGES
    elif request.get('service_type') == 'air_freight_local':
        charge_codes = AIR_FREIGHT_LOCAL_CHARGES
    else :
        charge_codes= AIR_FREIGHT_CHARGES
 

    commodity= request.get('commodity')
    commodity_type= request.get('commodity_type')
    commodity_sub_type= request.get('commodity_sub_type')

    
    response = {"list": []}
    for code, config in charge_codes.items():
        if "deleted" in config.get("tags"):
            continue
        if request.get('service_type') == 'air_freight_local' and request.get('trade_type') and request.get('trade_type') not in config.get("trade_types"):
            continue
        response["list"].append({
            "code": code,
            "name": config.get("name"),
            "units": config.get("units"),
            "condition": config.get("condition"),
            "tags": config.get("tags"),
            "trade_types": config.get("trade_types"),
            "sac_code": config.get("sac_code"),
        })
    return response

def validate(request):
    if (request.get('service_type')  not in ['air_freight', 'air_freight_surcharges', 'air_freight_local']):
        print(request.get('service_type'))
        raise HTTPException(status_code=400, detail="service type should be either air_freight or air_freight_surcharges or air_freight_local")



