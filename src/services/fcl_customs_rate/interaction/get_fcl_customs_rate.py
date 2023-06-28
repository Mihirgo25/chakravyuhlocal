from services.fcl_customs_rate.models.fcl_customs_rate import FclCustomsRate

def get_fcl_customs_rate(request):
    if not all_fields_present(request):
        return {}
    
    custom_object = find_object(request)

    params = get_object_params(request)

    if custom_object:
        detail = custom_object.detail()
    else:
        detail = {}

    customs_rate = FclCustomsRate(**params)
    detail['fcl_customs_charge_codes'] = customs_rate.possible_customs_charge_codes()
    detail['fcl_customs_cfs_charge_codes'] = customs_rate.possible_cfs_charge_codes()

    return detail
    
def all_fields_present(request):
    return request.get('location_id') and request.get('trade_type') and request.get('container_size') and request.get('container_type') and request.get('service_provider_id')

def find_object(request):
    object = FclCustomsRate.select(
        FclCustomsRate.customs_line_items, 
        FclCustomsRate.customs_line_items_info_messages, 
        FclCustomsRate.is_customs_line_items_info_messages_present, 
        FclCustomsRate.customs_line_items_error_messages, 
        FclCustomsRate.is_customs_line_items_error_messages_present, 
        FclCustomsRate.cfs_line_items, 
        FclCustomsRate.cfs_line_items_info_messages, 
        FclCustomsRate.is_cfs_line_items_info_messages_present, 
        FclCustomsRate.cfs_line_items_error_messages, 
        FclCustomsRate.is_cfs_line_items_error_messages_present
    ).where(
        FclCustomsRate.location_id == request.get('location_id'), 
        FclCustomsRate.trade_type == request.get('trade_type'), 
        FclCustomsRate.container_size == request.get('container_size'), 
        FclCustomsRate.container_type == request.get('container_type'), 
        FclCustomsRate.commodity == request.get('commodity'), 
        FclCustomsRate.service_provider_id == request.get('service_provider_id'), 
        FclCustomsRate.importer_exporter_id == request.get('importer_exporter_id')).first()
    return object

def get_object_params(request):
    params = {
        'location_id': request.get('location_id'),
        'trade_type': request.get('trade_type'),
        'container_size': request.get('container_size'),
        'container_type': request.get('container_type'),
        'commodity': request.get('commodity'),
        'service_provider_id': request.get('service_provider_id')
    }
    return params