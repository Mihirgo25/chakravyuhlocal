from configs.definitions import AIR_CUSTOMS_CHARGES
import json
from fastapi import HTTPException

def list_air_customs_charge_codes(request):
    # request = json.loads(request)
    validate_service_type(request)
    charges = get_charge_codes(request)
    if not charges:
        return {}
    
    return charges

def get_charge_codes(request):
    charge_codes = {code: config for code, config in AIR_CUSTOMS_CHARGES.items() if request.get('trade_type') in config['trade_types']}

    response = {}
    response['list'] = []

    for code, value in charge_codes.items():
        if 'deleted' in value.get('tags'):
            continue

        response['list'].append({ 'code': code, 'name': value['name'], 'units': value['units'], 'condition': value['condition'], 'tags': value['tags'], 'trade_types': value['trade_types'], 'sac_code': value.get('sac_code') })
    return response

def validate_service_type(request):
    if request.get('service_type') != 'air_customs':
        raise HTTPException(status_code=400, detail='Invalid Service Type')