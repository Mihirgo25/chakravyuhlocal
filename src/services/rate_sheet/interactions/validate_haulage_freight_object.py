import services.rate_sheet.interactions.validate_haulage_freight_object as validate_rate_sheet
from micro_services.client import *
from fastapi import HTTPException
from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate

# validate_validity_object
def validate_haulage_freight_object(module, object):
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

def get_freight_object(object):
    validation = {}
    rate_object = {}
    validation['error'] = ''
    res = object
    res['rate_not_available_entry'] = False
    rate_object = HaulageFreightRate(**res)
    try:
        rate_object.set_locations()
        rate_object.set_platform_price()
        rate_object.set_is_best_price()
    except HTTPException as e:
         validation['error']+=' ' + ' Invalid Locations'

    try:
        rate_object.validate_before_save()
    except HTTPException as e:
        validation['error']+=' ' + str(e.detail)

    try:
        rate_object.validate_validity_object(object['validity_start'], object['validity_end'])
    except HTTPException as e:
        validation['error']+=' ' + str(e.detail)

    return validation