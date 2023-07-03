import services.rate_sheet.interactions.validate_air_customs_object as validate_rate_sheet
from micro_services.client import maps
from services.air_customs_rate.models.air_customs_rate import AirCustomsRate
from fastapi import HTTPException
from configs.fcl_freight_rate_constants import RATE_TYPES,DEFAULT_RATE_TYPE

def validate_air_customs_object(module, object):
    response = {}
    response['valid'] = False
    try:
        rate_object = getattr(validate_rate_sheet, "get_{}_object".format(module))(object)
        if rate_object['error'].strip():
            response['error'] = rate_object['error']
        else:
            response['valid'] = True
    except Exception as e:
        response['error'] = e
    return response

def get_customs_object(object):
    res = {
        'airport_id': object.get('airport_id'),
        'trade_type': object.get('trade_type'),
        'commodity': object.get('commodity'),
        'service_provider_id': object.get('service_provider_id'),
        'importer_exporter_id': object.get('importer_exporter_id'),
        'rate_type':object.get('rate_type',DEFAULT_RATE_TYPE)
    }
    validation = {}
    validation['error'] = ''
    custom = AirCustomsRate(**res)

    if 'rate_type' in object and object['rate_type'] and object['rate_type'] not in RATE_TYPES:
        validation['error']+=  ' ' + f"{object['rate_type']} is invalid, valid rate types are {RATE_TYPES}"

    custom.line_items = object.get('line_items')
    try:
        custom.validate_before_save()
    except HTTPException as e:
        validation['error']+=' ' + str(e.detail)

    return validation