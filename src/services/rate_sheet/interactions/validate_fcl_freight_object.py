import services.rate_sheet.interactions.validate_fcl_freight_object as validate_rate_sheet
from libs.locations import list_locations
from micro_services.client import *
from operator import attrgetter
import uuid
from fastapi import HTTPException

# from services.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
import datetime
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from services.fcl_freight_rate.models.fcl_freight_rate_free_day import FclFreightRateFreeDay
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
    keys_to_extract = ['origin_port_id',
    'origin_main_port_id',
    'destination_port_id',
    'destination_main_port_id',
    'container_size',
    'container_type',
    'commodity',
    'shipping_line_id',
    'service_provider_id',
    'importer_exporter_id',
    'cogo_entity_id',
    'destination_local',
    'is_extended'
    ]
    res = dict(filter(lambda item: item[0] in keys_to_extract, object.items()))
    res['rate_not_available_entry'] = False
    rate_object = FclFreightRate(**res)
    if not rate_object.validate_origin_main_port_id():
        validation['error']+='Invalid origin main port'
    if not rate_object.validate_destination_main_port_id():
        validation['error']+='Invalid destination main port'
    if not rate_object.validate_container_size():
        validation['error']+='Invalid container '
    if not rate_object.validate_container_type():
        validation['error']+='Invalid container type'
    if not rate_object.validate_commodity():
        validation['error']+='Invalid commodity '
    try:
        rate_object.validate_before_save()
    except HTTPException as e:
        validation['error'] += str(e.detail)
    try:
        rate_object.validate_validity_object(object['validity_start'], object['validity_end'])
    except HTTPException as e:
        validation['error'] += str(e.detail)
    for line_item in object['line_items']:
        if not ( str(float(line_item['price'])) == line_item['price'] or str(int(line_item['price'])) == line_item['price']):
            validation['error']+= "line_item_price is invalid"
        if line_item['unit'] not in VALID_UNITS:
            validation['error']+=  "unit is_invalid"
    if object['schedule_type'] and object['schedule_type'] not in SCHEDULE_TYPES:
        validation['error'] += f"is invalid, valid schedule types are {SCHEDULE_TYPES}"
    if object['payment_term'] and object['payment_term'] not in PAYMENT_TERM:
        validation['error']+=  f"is invalid, valid payment terms are {PAYMENT_TERM}"
        validation['error']+=str(rate_object.validate_line_items(object['line_items']))
    return validation

def get_local_object(object):
    validation = {}
    keys_to_extract = ['port_id',
    'trade_type',
    'main_port_id',
    'container_size',
    'container_type',
    'commodity',
    'shipping_line_id',
    'service_provider_id']
    res = dict(filter(lambda item: item[0] in keys_to_extract, object.items()))
    local = FclFreightRateLocal(**res)
    if not local.validate_trade_type():
        validation['error']+='Invalid trade type'
    if not local.validate_main_port_id():
        validation['error']+='Invalid origin main port'
    if not local.validate_data():
        validation['error']+='Invalid data'
    if not local.validate_container_size():
        validation['error']+='Invalid container '
    if not local.validate_container_type():
        validation['error']+='Invalid container type'
    if not local.validate_commodity():
        validation['error']+='Invalid commodity '
    try:
        local.validate_before_save()
    except HTTPException as e:
        validation['error'] += str(e.detail)
    for line_item in object.get('data').get('line_items'):
        if not ( str(float(line_item['price'])) == line_item['price'] or str(int(line_item['price'])) == line_item['price']):
            validation['error']+="line_item_price is invalid"
        if line_item['unit'] not in VALID_UNITS:
            validation['error']+= "unit is_invalid"

    return validation

def get_free_day_object(object):
    error = {}
    try:
        location = get_location(object.get('location').get('port_code'), object.get('location_type'))[0]
        del object['location']
        object['location_id'] = location.get('id')
        object['port_id'] = location.get('seaport_id')
        object['country_id'] = location.get('country_id')
        object['trade_id'] = location.get('trade_id')
        object['continent_id'] = location.get('continent_id')
        object['shipping_line_id'] = get_shipping_line_id(object.get('shipping_line_id'))
        object['importer_exporter_id'] = get_importer_exporter_id(object.get('importer_exporter'))
        keys_to_extract = ['location_id',
        'trade_type',
        'container_size',
        'container_type',
        'shipping_line_id',
        'specificity_type',
        'free_days_type',
        'shipping_line_id',
        'service_provider_id',
        'importer_exporter_id']

        res = dict(filter(lambda item: item[0] in keys_to_extract, object.items()))
        free_day = FclFreightRateFreeDay(**res)
        if not is_valid_uuid(free_day.location_id):
            error['error'] = 'location is invalid'
        if not is_valid_uuid(free_day.shipping_line_id):
            error['error'] = 'shipping is invalid'
        # if free_day.specificity_type in SPECIFICITY_TYPE:
        #     error['error'] = 'specificity_type is invalid'
        free_day = free_day.__dict__['__data__']
    except Exception as e:
            error['error'] = e if 'error' not in error else error['error'] + e
    if 'error' in error:
        free_day['error'] = error['error']
    return free_day




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
