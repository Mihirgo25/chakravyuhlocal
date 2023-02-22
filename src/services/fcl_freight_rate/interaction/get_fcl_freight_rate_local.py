from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocals
from services.fcl_freight_rate.models.fcl_freight_rate import possible_charge_codes
from services.fcl_freight_rate.models.fcl_freight_rate import detail

def get_fcl_freight_rate_local(request):
    detail = {}

    object_params = {
    'port_id': request.port_id,
    'main_port_id': request.main_port_id,
    'trade_type': request.trade_type,
    'container_size': request.container_size,
    'container_type': request.container_type,
    'commodity': request.commodity,
    'shipping_line_id': request.shipping_line_id,
    'service_provider_id': request.service_provider_id,
    }
    
    if (request.port_id != None) & (request.trade_type != None) & (request.container_size != None) & (request.container_type != None) & (request.shipping_line_id != None) & (request.service_provider_id != None):
        object = find_object(request)

        if object:
            details = detail(object)

    return details.update({'local_charge_codes': possible_charge_codes(FclFreightRateLocals.get(object_params).dicts().get())})


def find_object(request):
    object = FclFreightRateLocals.select().where(FclFreightRateLocals.port_id == request.port_id, FclFreightRateLocals.main_port_id == request.main_port_id, FclFreightRateLocals.trade_type == request.trade_type, FclFreightRateLocals.container_size == request.container_size, FclFreightRateLocals.container_type == request.container_type, FclFreightRateLocals.commodity == request.commodity, FclFreightRateLocals.shipping_line_id == request.shipping_line_id, FclFreightRateLocals.service_provider_id == request.service_provider_id).limit(1).dicts().get()
    return object

