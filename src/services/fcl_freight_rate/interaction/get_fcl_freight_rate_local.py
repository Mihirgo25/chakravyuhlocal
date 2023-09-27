from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from libs.get_parsed_conditions import get_parsed_conditions_data
from configs.definitions import FCL_FREIGHT_LOCAL_CHARGES
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE

def get_fcl_freight_rate_local(request):
    details = {}
    if all_fields_present(request):
        object = find_object(request)
        if object:
          details = object.detail()
          if request['is_parsed'] and details.get('line_items'):
             old_line_items = details['line_items']
             parsed_line_items = get_parsed_conditions_data(old_line_items)
             details['line_items'] = parsed_line_items
    else:
      object=None

    if not object:
      object = FclFreightRateLocal()
      for key in list(request.keys()):
        setattr(object, key, request[key])
    return details | ({'local_charge_codes': object.possible_charge_codes()})


def find_object(request):
  if request.get('id'):
     object = FclFreightRateLocal.get_by_id(request['id'])
  elif request.get('rate_type') == 'cogo_assured':
      object = FclFreightRateLocal.select().where(
      FclFreightRateLocal.port_id == request.get("port_id"),
      FclFreightRateLocal.trade_type == request.get("trade_type"),
      FclFreightRateLocal.rate_type == 'cogo_assured'
      ).first()
  else:
    object_query = FclFreightRateLocal.select().where(
      FclFreightRateLocal.port_id == request.get("port_id"),
      FclFreightRateLocal.trade_type == request.get("trade_type"),
      FclFreightRateLocal.container_size == request.get("container_size"),
      FclFreightRateLocal.container_type == request.get('container_type'),
      FclFreightRateLocal.shipping_line_id == request.get("shipping_line_id"),
      FclFreightRateLocal.service_provider_id == request.get("service_provider_id"),
      FclFreightRateLocal.rate_type == DEFAULT_RATE_TYPE,
      FclFreightRateLocal.commodity == (request.get("commodity") or None),
      FclFreightRateLocal.main_port_id == (request.get("main_port_id") or None)
    )

    object = object_query.first()
  
  return object

def all_fields_present(object_params):
    if  (object_params.get('rate_type') == 'cogo_assured' and object_params.get('port_id') is not None and object_params.get('trade_type') is not None) or ((object_params['port_id'] is not None) and (object_params['trade_type'] is not None) and (object_params['container_size'] is not None) and (object_params['container_type'] is not None) and (object_params['shipping_line_id'] is not None) and (object_params['service_provider_id'] is not None) and (object_params.get('rate_type') is not None)) or (object_params['id'] is not None):
        return True
    return False