import services.rate_sheet.interactions.validate_fcl_freight_object as validate_rate_sheet
from micro_services.client import *
import uuid
from fastapi import HTTPException
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_free_day import get_free_day_object as get_free_day_objects
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
import datetime
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from configs.fcl_freight_rate_constants import VALID_UNITS, SCHEDULE_TYPES, PAYMENT_TERM, RATE_TYPES
from libs.common_validations import validate_shipping_line
from database.rails_db import get_operators, get_organization
from libs.get_normalized_line_items import get_normalized_line_items
from configs.definitions import FCL_FREIGHT_CURRENCIES

# validate_validity_object
def validate_fcl_freight_object(module, object):
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
    rate_object = FclFreightRate(**res)
    line_items = get_normalized_line_items(object['line_items'])
    
    if not rate_object.origin_port_id:
        validation['error']+=' Invalid origin port'
    if not rate_object.destination_port_id:
        validation['error']+=' Invalid destination port'
    try:
        rate_object.set_locations()
        rate_object.set_origin_location_ids()
        rate_object.set_destination_location_ids()
        rate_object.set_validities(object['validity_start'], object['validity_end'],line_items, object['schedule_type'], False, object['payment_term'])
    except:
        validation['error']+=' Invalid location'
    if validation['error'].strip():
        return validation
    try:
        rate_object.validate_before_save()
    except HTTPException as e:
        validation['error'] += ' ' + str(e.detail)
    try:
        rate_object.validate_validity_object(object['validity_start'], object['validity_end'])
    except HTTPException as e:
        validation['error'] += ' ' + str(e.detail)
    for line_item in line_items:
        if line_item['unit'] not in VALID_UNITS:
            validation['error'] =  ' ' + "unit is_invalid"
    if object['schedule_type'] and object['schedule_type'] not in SCHEDULE_TYPES:
        validation['error'] += ' ' + f"{object['schedule_type']} is invalid, valid schedule types are {SCHEDULE_TYPES}"

    if object['payment_term'] and object['payment_term'] not in PAYMENT_TERM:
        validation['error']+=  ' ' + f"{object['payment_term']} is invalid, valid payment terms are {PAYMENT_TERM}"
    
    if 'rate_type' in object and object['rate_type'] and object['rate_type'] not in RATE_TYPES:
        validation['error']+=  ' ' + f"{object['rate_type']} is invalid, valid rate types are {RATE_TYPES}"

    if rate_object.origin_port:
        origin_port_data = rate_object.origin_port
        if origin_port_data.get('is_icd') != True and rate_object.origin_main_port:
            validation['error']+= 'Main port cannot be assigned to a Base port (origin)' 
        
    if rate_object.destination_port:
        destination_port_data = rate_object.destination_port
        if destination_port_data.get('is_icd') != True and rate_object.destination_main_port:
            validation['error']+= 'Main port cannot be assigned to a Base port (destination)' 

    try:
        rate_object.validate_line_items(line_items)
    except HTTPException as e:
        validation['error']+=' ' + str(e.detail)
    if not validate_shipping_line(rate_object):
         validation['error']+=' Invalid shipping line'
    return validation

def get_local_object(object):
    validation = {}
    validation['error'] = ''
    res = object
    local = FclFreightRateLocal(**res)
    if not local.port_id:
        validation['error']+=' Invalid port'
    if validation['error'].strip():
        return validation
    try:
        local.validate_before_save()
    except HTTPException as e:
        validation['error'] += ' ' + str(e.detail)
        
    line_items = object.get('data', {}).get('line_items', [])
    
    if object.get('rate_type') == 'cogo_assured':
        if len(line_items) != 1:
            validation['error']+= ' ' + f"{len(line_items)} length of line_items is invalid for cogo assured rate"
        elif line_items[0]['code'] != 'THC':
            validation['error']+= ' ' + f"{line_items[0]['code']} code is invalid for cogo assured rate" 

    for line_item in line_items:
        if line_item['unit'] not in VALID_UNITS:
            validation['error']+= ' ' + "unit is_invalid"
        if line_item['currency'] not in FCL_FREIGHT_CURRENCIES.get():
            validation['error']+= ' ' + "currency is invalid"

    if not validate_shipping_line(local):
         validation['error']+=' Invalid shipping line'
    
    if local.port:
        port_data = local.port
        if port_data.get('is_icd') == False and local.main_port_id:        
            validation['error']+= 'Main port cannot be assigned to a Base port' 
        
    return validation

def get_free_day_object(object):
    validation = {}
    validation['error'] = ''
    res = object
    free_day = get_free_day_objects(res)
    try:
        free_day.validate_validity_object(object.get('validity_start'), object.get('validity_end'))
    except HTTPException as e:
        validation['error'] += ' ' + str(e.detail)
    try:
        free_day.validate_before_save()
    except HTTPException as e:
        validation['error'] += ' ' +str(e.detail)
    if not is_valid_uuid(free_day.location_id):
        validation['error'] += ' location {} is invalid'.format(free_day.location_id)
    if not is_valid_uuid(free_day.shipping_line_id):
        validation['error'] += ' shipping {} is  invalid'.format(free_day.shipping_line_id)
    # if free_day.specificity_type in SPECIFICITY_TYPE:
    #     validation['error'] += 'specificity_type is invalid'

    return validation




def get_location(location, type):
    if type == 'port':
        filters =  {'filters': {"type": "seaport", "port_code": location, "status": "active"}}
        location =  maps.list_locations(filters)['list']
    else:
        filters =  {'filters': {"type": "seaport", "name": location, "status": "active"}}
        location =  maps.list_locations(filters)['list']
    if location:
        return location
    else:
        return None


def get_port_id(port_code):
    filters =  {'filters':{"type": "seaport", "port_code": port_code, "status": "active"}}
    try:
        port_id =  maps.list_locations(filters)['list'][0]["id"]
    except:
        port_id = None
    return port_id

def get_shipping_line_id(shipping_line_name):
    try:
        shipping_line_id = get_operators(short_name=shipping_line_name)[0]['id']
    except:
        shipping_line_id = None
    return shipping_line_id

def get_location_id(query):
    filters =  {"type": "seaport", "port_code": query, "status": "active"}
    port_id = maps.list_locations({'filters': filters})['list']
    if not port_id:
        filters =  {"type": "country", "country_code": query, "status": "active"}
        port_id =  maps.list_locations({'filters': filters})['list']
    if not port_id:
        filters =  {"type": "seaport", "port_code": query, "status": "active"}
        port_id =  maps.list_locations({'filters': filters})['list']
    if not port_id:
        filters =  {"name": query}
        port_id =  maps.list_locations({'filters': filters})['list']
    if port_id:
        return port_id[0]['id']
    else:
        return None


def get_importer_exporter_id(importer_exporter_name):
    try:
        importer_exporter_id = get_organization(short_name=importer_exporter_name)[0]['id']
    except:
        importer_exporter_id = None
    return importer_exporter_id

def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False
