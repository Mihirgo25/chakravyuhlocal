from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from configs.definitions import FCL_FREIGHT_LOCAL_CHARGES
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE

def get_fcl_freight_rate_local_conditions_data(request):
  details = {}
  conditional_data = []
  object = find_object(request)
  data = object.data
  # if data.get('line_items'):
  #    for item in data['line_items']:
  #       if item.get('conditions'):
           
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