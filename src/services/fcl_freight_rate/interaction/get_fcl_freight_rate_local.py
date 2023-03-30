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
    return details | ({'local_charge_codes': object.possible_charge_codes() if object else FCL_FREIGHT_LOCAL_CHARGES})


def find_object(request):
  try:
    object = FclFreightRateLocal.get(**request)
  except: 
    object = None
    return object

def all_fields_present(object_params):
  if (object_params['port_id'] is not None) and (object_params['trade_type'] is not None) and (object_params['container_size'] is not None) and (object_params['container_type'] is not None) and (object_params['shipping_line_id'] is not None) and (object_params['service_provider_id'] is not None):
    return True
  return False