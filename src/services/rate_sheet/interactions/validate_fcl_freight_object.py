import services.rate_sheet.interactions.validate_fcl_freight_object as validate_rate_sheet
from micro_services.client import *
import uuid
from fastapi import HTTPException
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_free_day import get_free_day_object as get_free_day_objects
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
import datetime
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from configs.fcl_freight_rate_constants import VALID_UNITS, SCHEDULE_TYPES, PAYMENT_TERM, SPECIFICITY_TYPE

from database.rails_db import get_shipping_line, get_organization

# validate_validity_object
def validate_fcl_freight_object(module, object):
    response = {}
    response['valid'] = False
    try:
        rate_object = getattr(validate_rate_sheet, "get_{}_object".format(module))(object)
        if rate_object['error'].strip() != '':
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
    try:
        rate_object.set_locations()
        rate_object.set_origin_location_ids()
        rate_object.set_destination_location_ids()
        rate_object.set_validities(object['validity_start'], object['validity_end'],object['line_items'], object['schedule_type'], False, object['payment_term'])
    except:
        validation['error']+='Invalid location'
    try:
        rate_object.validate_before_save()
    except HTTPException as e:
        validation['error'] += str(e.detail)
    try:
        rate_object.validate_validity_object(object['validity_start'], object['validity_end'])
    except HTTPException as e:
        validation['error'] += str(e.detail)
    for line_item in object['line_items']:
        if line_item['unit'] not in VALID_UNITS:
            validation['error'] =  "unit is_invalid"
    if object['schedule_type'] and object['schedule_type'] not in SCHEDULE_TYPES:
        validation['error'] += f"{object['schedule_type']} is invalid, valid schedule types are {SCHEDULE_TYPES}"

    if object['payment_term'] and object['payment_term'] not in PAYMENT_TERM:
        validation['error']+=  f"{object['payment_term']} is invalid, valid payment terms are {PAYMENT_TERM}"
    try:
        rate_object.validate_line_items(object['line_items'])
    except HTTPException as e:
        validation['error']+=str(e.detail)
    return validation

def get_local_object(object):
    validation = {}
    validation['error'] = ''
    res = object
    local = FclFreightRateLocal(**res)
    try:
        local.validate_before_save()
    except HTTPException as e:
        validation['error'] += str(e.detail)
    for line_item in object.get('data').get('line_items'):
        if line_item['unit'] not in VALID_UNITS:
            validation['error']+= "unit is_invalid"

    return validation

def get_free_day_object(object):
    validation = {}
    validation['error'] = ''
    res = object
    free_day = get_free_day_objects(res)
    try:
        free_day.validate_validity_object(object.get('validity_start'), object.get('validity_end'))
    except HTTPException as e:
        validation['error'] += str(e.detail)
    try:
        free_day.validate_before_save()
    except HTTPException as e:
        validation['error'] += str(e.detail)
    if not is_valid_uuid(free_day.location_id):
        validation['error'] += 'location is invalid'
    if not is_valid_uuid(free_day.shipping_line_id):
        validation['error'] += 'shipping is invalid'
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
        shipping_line_id = get_shipping_line(short_name=shipping_line_name)[0]['id']
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
