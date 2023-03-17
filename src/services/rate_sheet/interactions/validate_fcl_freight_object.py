import services.rate_sheet.interactions.validate_fcl_freight_object as validate_rate_sheet
from libs.locations import list_locations
from rails_client import client
# from services.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
import datetime
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
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
    for port in ['origin_port', 'origin_main_port', 'destination_port', 'destination_main_port']:
        object[f'{port}_id'] = get_port_id(object[port])
        del object[port]
    object['shipping_line_id'] = get_shipping_line_id(object['shipping_line_id'])
    del object['shipping_line_id']
    object['validity_start'] = object['validity_start']
    try:
        object['validity_start'] = datetime.datetime.strptime(object['validity_start'], '%Y-%m-%d').date()
    except ValueError:
        object['validity_start'] = None
    try:
        object['validity_end'] = datetime.datetime.strptime(object['validity_end'], '%Y-%m-%d').date()
    except ValueError:
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
    rate_object.weight_limit = object['weight_limit']
    rate_object.destination_local['']
    return rate_object

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
