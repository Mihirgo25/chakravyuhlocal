from services.fcl_freight_rate.models.fcl_freight_rate_free_day import FclFreightRateFreeDay
from fastapi import HTTPException


def get_fcl_freight_rate_free_day(request):
    if not all_fields_present(request):
        return {}
    
    objects = find_object(request)
    if not objects:
        return {}
    
    objects = objects.detail()
    return objects

def all_fields_present(request):
    if request['location_id'] and request['trade_type'] and request['free_days_type'] and request['container_size'] and request['container_type'] and request['shipping_line_id'] and request['service_provider_id']:
        return True
    return False

def find_object(request):
    row = {
        'location_id' : request['location_id'],
        'trade_type' : request['trade_type'],
        'free_days_type' : request['free_days_type'],
        'container_type' : request['container_type'],
        'container_size' : request['container_size'],
        'shipping_line_id' : request['shipping_line_id'],
        'service_provider_id' : request['service_provider_id'],
        'importer_exporter_id' : request.get('importer_exporter_id')
    }
    
    try:
        objects = FclFreightRateFreeDay.get(**row)
    except:
        raise HTTPException(status_code=403, detail="no free day entry with the given id exists")
    return objects