import services.rate_sheet.interactions.validate_fcl_freight_object as validate_rate_sheet
from libs.locations import list_locations
from rails_client import client
# from services.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
import datetime
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from services.fcl_freight_rate.models.fcl_freight_rate_free_day import FclFreightRateFreeDay
from services.fcl_freight_rate.helpers.find_or_initialize import find_or_initialize
# from services.fcl_freight_rate.models.fcl_freight_rate import
VALID_UNITS = ['per_bl', 'per_container', 'per_shipment']
SCHEDULE_TYPES = ['direct', 'transhipment']
PAYMENT_TERM = []

# validate_validity_object
def validate_fcl_freight_object(module, object):
    rate_object = getattr(validate_rate_sheet, "get_{}_object".format(module))(object)
    return

def get_freight_object(object):
    print(object)
    for port in ['origin_port', 'origin_main_port', 'destination_port', 'destination_main_port']:
        object[f'{port}_id'] = get_port_id(object.get(port))
        del object[port]
    object['shipping_line_id'] = get_shipping_line_id(object.get('shipping_line_id'))
    del object['shipping_line_id']
    object['validity_start'] = object['validity_start']
    try:
        object['validity_start'] = datetime.datetime.strptime(object.get('validity_start'), '%Y-%m-%d').date()
    except:
        object['validity_start'] = None
    try:
        object['validity_end'] = datetime.datetime.strptime(object.get('validity_end'), '%Y-%m-%d').date()
    except :
        object['validity_end'] = None
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
      'cogo_entity_id']
    res = dict(filter(lambda item: item[0] in keys_to_extract, object.items()))
    res['rate_not_available_entry'] = False
    rate_object = find_or_initialize(FclFreightRate,**res)
    rate_object.validate_validity_object(object['validity_start'], object['validity_end'])
    for line_item in object['line_items']:
        if not ( str(float(line_item['price'])) == line_item['price'] or str(int(line_item['price'])) == line_item['price']):
            return "line_item_price is invalid"
        if line_item['unit'] not in VALID_UNITS:
            return "unit is_invalid"
    if 'schedule_type' in object and object['schedule_type'] not in SCHEDULE_TYPES:
        return f"is invalid, valid schedule types are {SCHEDULE_TYPES}"
    if 'payment_term' in object and object['payment_term'] not in PAYMENT_TERM:
        return f"is invalid, valid payment terms are {PAYMENT_TERM}"
    rate_object.validate_line_items(object['line_items'])
    rate_object.weight_limit = object.get('weight_limit')
    # rate_object.destination_local['']
    print(rate_object, "final_object")
    return rate_object

def get_local_object(object):
    for port in ['port', 'main_port']:
        object[f'{port}_id'] = get_port_id(object[port])
        del object[port]

    for line_item in object.get('data').get('line_items'):
        line_item['location_id'] = get_location_id(line_item.get('location'))
        del line_item['location']
    object['shipping_line_id'] = get_shipping_line_id(object.get('shipping_line_id'))
    del object['shipping_line_id']

    keys_to_extract = ['port_id',
      'trade_type',
      'main_port_id',
      'container_size',
      'container_type',
      'commodity',
      'shipping_line_id',
      'service_provider_id']
    res = dict(filter(lambda item: item[0] in keys_to_extract, object.items()))
    local = find_or_initialize(FclFreightRateLocal,**res)
    for line_item in object.get('data').get('line_items'):
        if not ( str(float(line_item['price'])) == line_item['price'] or str(int(line_item['price'])) == line_item['price']):
            return "line_item_price is invalid"
        if line_item['unit'] not in VALID_UNITS:
            return "unit is_invalid"
    return local

def get_free_day_object(object):
    location = get_location(object['location'], object['location_type'])
    object['location_id'] = location.get('id')
    object['port_id'] = location.get('seaport_id')
    object['country_id'] = location.get('country_id')
    object['trade_id'] = location.get('trade_id')
    object['continent_id'] = location.get('continent_id')
    del object['location']
    object['shipping_line_id'] = get_shipping_line_id(object.get('shipping_line'))
    del object['shipping_line']
    object['importer_exporter_id'] = get_importer_exporter_id(object.get('importer_exporter'))
    del object['importer_exporter']
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
    free_day = find_or_initialize(FclFreightRateFreeDay,**res)
    for key, val in object:
        free_day[key] = val
    # if object.get('location_id'):
    # will have to figure out how ot add error here
    return free_day




def get_location(location, type):
    if type == 'port':
        filters =  {"type": "seaport", "port_code": location, "status": "active"}
        location =  list_locations(filters)['list']
    else:
        filters =  {"type": "seaport", "name": location, "status": "active"}
        location =  list_locations(filters)['list']
    if location:
        return location
    else:
        return None


def get_port_id(port_code):
    filters =  {"type": "seaport", "port_code": port_code, "status": "active"}
    try:
        port_id =  list_locations({'filters': str(filters)})['list'][0]["id"]
    except:
        port_id = None
    return port_id

def get_shipping_line_id(shipping_line_name):
    shipping_line_id = client.ruby.list_operators(
        {
            "filters": {
                "operator_type": "shipping_line",
                "short_name": shipping_line_name,
                "status": "active",
            }
        }
    )["list"][0]['id']
    return shipping_line_id

def get_location_id(query):
    filters =  {"type": "seaport", "port_code": query, "status": "active"}
    port_id =  list_locations({'filters': str(filters)})['list']
    if not port_id:
        filters =  {"type": "country", "country_code": query, "status": "active"}
        port_id =  list_locations({'filters': str(filters)})['list']
    if not port_id:
        filters =  {"type": "seaport", "port_code": query, "status": "active"}
        port_id =  list_locations({'filters': str(filters)})['list']
    if not port_id:
        filters =  {"name": query}
        port_id =  list_locations({'filters': str(filters)})['list']
    if port_id:
        return port_id[0]['id']
    else:
        return None


def get_importer_exporter_id(importer_exporter_name):
    importer_exporter_id = client.ruby.list_organizations(
        {
            "filters": {
                "account_type": "importer_exporter",
                "short_name": importer_exporter_name,
                "status": "active",
            }
        }
    )["list"][0]
    return importer_exporter_id

