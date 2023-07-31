import services.rate_sheet.interactions.validate_fcl_cfs_object as validate_rate_sheet
from micro_services.client import maps
from services.fcl_cfs_rate.models.fcl_cfs_rate import FclCfsRate
from fastapi import HTTPException
from configs.fcl_freight_rate_constants import RATE_TYPES,DEFAULT_RATE_TYPE

def validate_fcl_cfs_object(module, object):
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

def get_cfs_object(object):
    res = {
        'location_id': object.get('location_id'),
        'trade_type': object.get('trade_type'),
        'container_size': object.get('container_size'),
        'container_type': object.get('container_type'),
        'commodity': object.get('commodity'),
        'service_provider_id': object.get('service_provider_id'),
        'importer_exporter_id': object.get('importer_exporter_id'),
        'cargo_handling_type': object.get('cargo_handling_type'),
        'rate_type':object.get('rate_type',DEFAULT_RATE_TYPE)
    }
    validation = {}
    validation['error'] = ''
    cfs_rate = FclCfsRate(**res)

    if 'rate_type' in object and object['rate_type'] and object['rate_type'] not in RATE_TYPES:
        validation['error']+=  ' ' + f"{object['rate_type']} is invalid, valid rate types are {RATE_TYPES}"

    cfs_rate.line_items = object.get('line_items')
    cfs_rate.free_days = object.get('free_days')

    try:
        cfs_rate.validate_before_save()
        cfs_rate.validate_mandatory_free_days()
    except HTTPException as e:
        validation['error']+=' ' + str(e.detail)

    return validation