import services.rate_sheet.interactions.validate_ftl_freight_object as validate_rate_sheet
from services.ftl_freight_rate.models.ftl_freight_rate import FtlFreightRate
from micro_services.client import *
from fastapi import HTTPException

def validate_ftl_freight_object(module, object):
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
    res = {
        'origin_location_id': object.get('origin_location_id'),
        'destination_location_id': object.get('destination_location_id'),
        'truck_type': object.get('truck_type'),
        'truck_body_type': object.get('truck_body_type'),
        'commodity': object.get('commodity'),
        'service_provider_id': object.get('service_provider_id'),
        'importer_exporter_id': object.get('importer_exporter_id'),
        'transit_time': object.get('transit_time'),
        'detention_free_time': object.get('detention_free_time'),
        'trip_type': object.get('trip_type')
    }


    object['origin_location_id'] = get_location_id(object['origin_location'])
    del object['origin_location']

    object['destination_location_id'] = get_location_id(object['destination_location'])
    del object['destination_location']

    freight = FtlFreightRate.select().where(
        FtlFreightRate.origin_location_id == object.get('origin_location_id'),
        FtlFreightRate.destination_location_id == object.get('destination_location_id'),
        FtlFreightRate.truck_type == object.get('truck_type'),
        FtlFreightRate.truck_body_type == object.get('truck_body_type'),
        FtlFreightRate.commodity == object.get('commodity'),
        FtlFreightRate.service_provider_id == object.get('service_provider_id'),
        FtlFreightRate.importer_exporter_id == object.get('importer_exporter_id'),
        FtlFreightRate.transit_time == object.get('transit_time'),
        FtlFreightRate.detention_free_time == object.get('detention_free_time'),
        FtlFreightRate.trip_type == object.get('trip_type')
    ).first()

    validation = {}
    validation['error'] = ''

    if not freight:
        freight = FtlFreightRate(**res)

    freight.line_items = object['line_items']
    freight.transit_time = object['transit_time']
    freight.detention_free_time = object['detention_free_time']
    freight.trip_type = object['trip_type']

    freight.validity_start = object['validity_start']
    freight.validity_end = object['validity_end']

    try:
        freight.validate_validities(object['validity_start'], object['validity_end'])
    except HTTPException as e:
        validation['error']+=' ' + str(e.detail)

    for line_item in object['line_items']:
        if not (str(float(line_item['price'])) == line_item['price'] or str(int(line_item['price'])) == line_item['price']):
            validation['error'] += "line item price is invalid"
    return validation

def get_location_id(query):
    filters =  {"type": "pincode", "postal_code": query, "status": "active"}
    port_id = maps.list_locations({'filters': filters})['list']
    if not port_id:
        filters = {"type": "city", "name": query, "status": "active"}
        port_id =  maps.list_locations({'filters': filters})['list']
    if not port_id:
        filters = {"type": "city", "display_name": query, "status": "active"}
        port_id =  maps.list_locations({'filters': filters})['list']
    if not port_id:
        filters = {"type": ["seaport", "airport"], "port_code": query, "status": "active"}
        port_id =  maps.list_locations({'filters': filters})['list']
    if port_id:
        return port_id[0]['id']
    else:
        return None
