from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from configs.global_constants import HAZ_CLASSES
from peewee import JOIN
from operator import attrgetter

def get_fcl_freight_rate(request):
  details = {}

  if all_fields_present(request):
    object = find_object(request)
    if object:
      details = object.detail()

  origin_local_object_params = {
    'port_id': request['origin_port_id'],
    'main_port_id': request['origin_main_port_id'],
    'trade_type': 'export',
    'container_size':request['container_size'],
    'container_type': request['container_type'],
    'shipping_line_id': request['shipping_line_id'],
    'service_provider_id': request['service_provider_id']
    }

  destination_local_object_params = {
    'port_id': request['destination_port_id'],
    'main_port_id': request['destination_main_port_id'],
    'trade_type': 'import',
    'container_size': request['container_size'],
    'container_type': request['container_type'],
    'shipping_line_id': request['shipping_line_id'],
    'service_provider_id': request['service_provider_id']
    }
  
  if request['commodity'] in HAZ_CLASSES:
    origin_local_object_params['commodity'] = request['commodity']
    destination_local_object_params['commodity'] = request['commodity']
  else:
    origin_local_object_params['commodity'] = None
    destination_local_object_params['commodity'] = None


  return details | ({
    'freight_charge_codes': (FclFreightRate(**request).possible_charge_codes()),
    'origin_local_charge_codes': (FclFreightRateLocal(**origin_local_object_params).possible_charge_codes()),
    'destination_local_charge_codes': (FclFreightRateLocal(**destination_local_object_params).possible_charge_codes())
  })


def find_object(object_params):
  query = FclFreightRate.select()
  port_origin_local = FclFreightRateLocal.select().alias('port_origin_local')
  port_destination_local = FclFreightRateLocal.select().alias('port_destination_local')
  for key in object_params:
    query = query.where(attrgetter(key)(FclFreightRate) == object_params[key])
  
  object = query.join(port_origin_local, JOIN.LEFT_OUTER, on = (FclFreightRate.origin_local_id == port_origin_local.c.id)).switch(
    FclFreightRate).join(port_destination_local, JOIN.LEFT_OUTER, on = (FclFreightRate.destination_local_id == port_destination_local.c.id)).first()
  return object 

def all_fields_present(object_params):
  if (object_params['origin_port_id'] is not None) and (object_params['destination_port_id'] is not None) and (object_params['container_size'] is not None) and (object_params['container_type'] is not None) and (object_params['shipping_line_id'] is not None) and (object_params['service_provider_id'] is not None):
    return True
  return False