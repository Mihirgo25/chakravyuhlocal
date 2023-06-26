from services.air_customs_rate.models.air_customs_rate import AirCustomsRate

def get_air_customs_rate(request):
    if not all_fields_present(request):
        return {}
    
    air_custom_object = find_object(request)
    if air_custom_object:
        detail = air_custom_object.detail()
    else:
        detail = {}

    return detail
    
def all_fields_present(request):
    return request.get('airport_id') and request.get('trade_type') and request.get('service_provider_id')

def find_object(request):
    object = AirCustomsRate.select(
    ).where(
        AirCustomsRate.airport_id == request.get('airport_id'), 
        AirCustomsRate.trade_type == request.get('trade_type'), 
        AirCustomsRate.commodity == request.get('commodity'), 
        AirCustomsRate.service_provider_id == request.get('service_provider_id'), 
        AirCustomsRate.importer_exporter_id == request.get('importer_exporter_id')).first()
    return object