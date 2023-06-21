import services.rate_sheet.interactions.validate_air_freight_object as validate_rate_sheet
from micro_services.client import *
import uuid
from fastapi import HTTPException
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
from services.air_freight_rate.models.air_freight_rate_surcharge import AirFreightRateSurcharge

def validate_air_freight_object(module, object):
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
    rate_object = AirFreightRate(**res)
    rate_object.length = 300
    rate_object.breadth = 300
    rate_object.height = 300
    rate_object.price_type = object.get('price_type')

    try:
        rate_object.validate_validity_object(object['validity_start'], object['validity_end'])
    except HTTPException as e:
        validation['error'] += ' ' + str(e.detail)

    if not is_float(object.get('min_price')):
        validation['error'] += ' min_price is invalid'

    
    for weight_slab in object['weight_slabs']:
        if not is_float(weight_slab.get('lower_limit')):
            validation['error'] += ' lower_limit is invalid'
        else:
            weight_slab["lower_limit"] = float(weight_slab['lower_limit'])
            
        if not is_float(weight_slab.get('upper_limit')):
            validation['error'] += ' upper_limit is invalid'
        else:
            weight_slab["upper_limit"] = float(weight_slab['upper_limit'])

        if not is_float(weight_slab.get('tariff_price')):
            validation['error'] += ' tariff_price is invalid'
        else:
            weight_slab["tariff_price"] = float(weight_slab['tariff_price'])
    
    # final_weight_slabs = object['weight_slabs']
    try:
        rate_object.set_validities(object["validity_start"], object["validity_end"], object["min_price"], object["currency"], object["weight_slabs"], object["deleted"], object["validity_id"], object["density_category"], object["density_ratio"], object["initial_volume"], object["initial_gross_weight"], object["available_volume"], object["available_gross_weight"], object["rate_type"])
    except HTTPException as e:
         validation['error'] += ' ' + str(e.detail)
    # try:
    #     rate_object.validate_before_save()
    # except HTTPException as e:
    #     validation['error'] += ' ' + str(e.detail)

    return validation

def get_local_object(object):
    validation = {}
    rate_object = {}
    validation['error'] = ''
    res = object
    res['rate_not_available_entry'] = False
    rate_object = AirFreightRateLocal(**res)
    try:
        rate_object.validate()
    except HTTPException as e:
         validation['error'] += ' ' + str(e.detail)

    return validation

def get_surcharge_object(object):
    validation = {}
    rate_object = {}
    validation['error'] = ''
    res = object
    res['rate_not_available_entry'] = False
    rate_object = AirFreightRateSurcharge(**res)

    try:
        rate_object.validate()
    except HTTPException as e:
         validation['error'] += ' ' + str(e.detail)

    return validation

    
def is_float(value):
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False

def get_airport_id(port_code, country_code):
    filters =  {"type": "airport", "port_code": port_code, "country_code": country_code, "status": "active"}
    port_id = maps.list_locations({'filters': filters})['list']
    if port_id:
        return port_id[0]['id']