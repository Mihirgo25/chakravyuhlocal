from micro_services.client import maps
from database.rails_db import get_operators
from services.air_freight_rate.models.air_freight_rate_surcharge import AirFreightRateSurcharge

def validate_air_freight_object(request):
    rate_object = eval("get_{}_object".format(request.get('module')))
    return
def get_freight_object(request):
    return

def get_local_object(request):
    return


def get_surcharge_object(object):
    object['origin_airport_id'] = get_airport_id(object.get('origin_airport'),object.get('origin_country'))
    object['destination_airport_id'] = get_airport_id(object.get('destination_airport'),object.get('destination_country'))
    object['airline_id'] = get_airline_id(object.get('airline'))
    row = {
        'origin_airport_id':object.get('origin_airport_id'),
        'destination_airport_id':object.get('destination_airport_id'),
        'airline_id':object.get('airline_id'),
        'operation_type':object.get('operation_type'),
        'commodity':object.get('commodity'),
        'commodity_type':object.get('commodity_type'),
        'service_provider_id':object.get('service_provider_id')
    }
    surchage = AirFreightRateSurcharge.select().where(**row).first()
    surchage.line_items = object.get('line_items')
    return surchage

def get_object_unique_params(object):
    params = {
        'origin_airport_id':object.get('origin_airport_id'),
        'destination_airport_id':object.get('destination_airport_id'),
        'airline_id':object.get('airline_id'),
        'operation_type':object.get('operation_type'),
        'commodity':object.get('commodity'),
        'commodity_type':object.get('commodity_type'),
        'commodity_sub_type':object.get('commodity_sub_type'),
        'service_provider_id':object.get('service_provider_id'),
        'price_type':object.get('price_type'),
        'cogo_entity_id':object.get('cogo_entity_id'),
        'rate_type':object.get('rate_type'),
        'source':object.get('source')

    }

    params['shipment_type'] = object.get('packing_type')
    params['stacking_type'] = object.get('handling_type')

    return params
def get_airport_id(port_code,country_code):
    airport = maps.list_locations({ "filters": { "type": 'airport', "port_code": port_code, "country_code": country_code, "status": 'active' }})['list'][0]
    return airport['id']

def get_airline_id(airline_name):
    try:
        airline_id = get_operators(short_name=airline_name,operator_type='airline')[0]['id']
    except:
        airline_id = None
    return airline_id

def is_float(val):
    try:
        float(val)
        return True
    except ValueError:
        return False

