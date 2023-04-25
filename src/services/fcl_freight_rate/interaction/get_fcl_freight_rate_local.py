from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from configs.definitions import FCL_FREIGHT_LOCAL_CHARGES
def get_fcl_freight_rate_local(request):
    details = {}

    if all_fields_present(request):
        object = find_object(request)
        if object:
          details = object.detail()
    else:
      object=None
    if not object:
      object = FclFreightRateLocal()
      for key in list(request.keys()):
        setattr(object, key, request[key])
    return details | ({'local_charge_codes': object.possible_charge_codes()})


def find_object(request):
 
  object = FclFreightRateLocal.select().where(
    FclFreightRateLocal.port_id == request.get("port_id"),
    FclFreightRateLocal.main_port_id == request.get("main_port_id"),
    FclFreightRateLocal.trade_type == request.get("trade_type"),
    FclFreightRateLocal.container_size == request.get("container_size"),
    FclFreightRateLocal.container_type == request.get('container_type'),
    FclFreightRateLocal.commodity == request.get("commodity"),
    FclFreightRateLocal.shipping_line_id == request.get("shipping_line_id"),
    FclFreightRateLocal.service_provider_id == request.get("service_provider_id")
  ).first()
  
  return object

def all_fields_present(object_params):
    if (object_params['port_id'] is not None) and (object_params['trade_type'] is not None) and (object_params['container_size'] is not None) and (object_params['container_type'] is not None) and (object_params['shipping_line_id'] is not None) and (object_params['service_provider_id'] is not None):
        return True
    return False