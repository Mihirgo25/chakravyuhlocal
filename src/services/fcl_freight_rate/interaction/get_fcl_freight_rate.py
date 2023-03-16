from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from configs.global_constants import HAZ_CLASSES
from peewee import JOIN
from operator import attrgetter

def get_fcl_freight_rate(origin_port_id, origin_main_port_id, destination_port_id, destination_main_port_id, container_size, container_type, commodity, shipping_line_id, service_provider_id, importer_exporter_id):
  detail = {}

  object_params = {
    'origin_port_id': origin_port_id,
    'origin_main_port_id': origin_main_port_id,
    'destination_port_id': destination_port_id,
    'destination_main_port_id': destination_main_port_id,
    'container_size': container_size,
    'container_type': container_type,
    'commodity': commodity,
    'shipping_line_id': shipping_line_id,
    'service_provider_id': service_provider_id,
    'importer_exporter_id': importer_exporter_id
  }

  if all_fields_present(object_params):
    object = find_object(object_params)
    detail = object.detail()

  origin_local_object_params = {
    'port_id': origin_port_id,
    'main_port_id': origin_main_port_id,
    'trade_type': 'export',
    'container_size': container_size,
    'container_type': container_type,
    'shipping_line_id': shipping_line_id,
    'service_provider_id': service_provider_id
    }

  destination_local_object_params = {
    'port_id': origin_port_id,
    'main_port_id': origin_main_port_id,
    'trade_type': 'export',
    'container_size': container_size,
    'container_type': container_type,
    'shipping_line_id': shipping_line_id,
    'service_provider_id': service_provider_id
    }
  
  if commodity in HAZ_CLASSES:
    origin_local_object_params['commodity'] = commodity
    destination_local_object_params['commodity'] = commodity
  else:
    origin_local_object_params['commodity'] = None
    destination_local_object_params['commodity'] = None


  return detail | ({
    'freight_charge_codes': (FclFreightRate(object_params).possible_charge_codes()),
    'origin_local_charge_codes': (FclFreightRateLocal(origin_local_object_params).possible_charge_codes()),
    'destination_local_charge_codes': (FclFreightRateLocal(destination_local_object_params).possible_charge_codes())
  })


def find_object(object_params):
  query = FclFreightRate.select()
  post_origin_locals = FclFreightRateLocal.select().alias('post_origin_locals')
  post_destination_locals = FclFreightRateLocal.select().alias('post_destination_locals')
  for key in object_params:
    query = query.where(attrgetter(key)(FclFreightRate) == object_params[key])
  
  object = query.join(post_origin_locals, JOIN.LEFT_OUTER, on = (FclFreightRate.origin_local_id == post_origin_locals.c.id)).switch(
    FclFreightRate).join(post_destination_locals, JOIN.LEFT_OUTER, on = (FclFreightRate.destination_local_id == post_destination_locals.c.id)).limit(1).execute()

  return object

def all_fields_present(object_params):
  if (object_params['origin_port_id'] is not None) and (object_params['destination_port_id'] is not None) and (object_params['container_size'] is not None) and (object_params['container_type'] is not None) and (object_params['shipping_line_id'] is not None) and (object_params['service_provider_id'] is not None):
    return True
  else:
    return False