import services.rate_sheet.interactions.validate_fcl_customs_object as validate_rate_sheet
from micro_services.client import maps
from services.fcl_customs_rate.models.fcl_customs_rate import FclCustomsRate
from fastapi import HTTPException

def validate_fcl_customs_object(module, object):
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

def get_customs_object(object):
    object['location_id'] = get_location_id(object.get('location'))
    if object.get('location'):
        del object['location']

    for line_item in object.get('customs_line_items'):
        line_item['location_id'] = get_location_id(line_item.get('location'))
        if line_item.get('location'):
            del line_item['location']

    for line_item in object.get('cfs_line_items'):
        line_item['location_id'] = get_location_id(line_item.get('location'))
        if line_item.get('location'):
            del line_item['location']

    res = {
        'location_id': object.get('location_id'),
        'trade_type': object.get('trade_type'),
        'container_size': object.get('container_size'),
        'container_type': object.get('container_type'),
        'commodity': object.get('commodity'),
        'service_provider_id': object.get('service_provider_id'),
        'importer_exporter_id': object.get('importer_exporter_id')
    }
    validation = {}
    validation['error'] = ''
    custom = FclCustomsRate(**res)
    # for line_item in object.get('customs_line_items'):
    #     print(line_item['price'])
    #     if not (str(float(line_item['price'])) == line_item['price'] or str(int(line_item['price'])) == line_item['price']):
    #         print('errorrrrr')
    #         validation['error'] += 'is_invalid'
    custom.customs_line_items = object.get('customs_line_items')
    custom.cfs_line_items = object.get('cfs_line_items')
    try:
        custom.validate_invalid_line_items()
    except HTTPException as e:
        validation['error']+=' ' + str(e.detail)

    return validation

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