from services.fcl_freight_rate.models.fcl_freight_rate_free_day import FclFreightRateFreeDay
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit


def get_fcl_freight_rate_free_day(request):
    if not all_fields_present(request):
        return {}
    
    object = find_object(request).__dict__

    if object is None:
        return {}
    print('object',object['__data__'])
    return object['__data__']

def all_fields_present(request):
    for field in (
        'location_id',
        'trade_type',
        'free_days_type',
        'container_size',
        'container_type',
        'shipping_line_id',
        'service_provider_id'
    ):
        if field not in request:
            return False
    return True

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
    # should we use try and except
    object = FclFreightRateFreeDay.get(**row)
    return object