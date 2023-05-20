from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from playhouse.shortcuts import model_to_dict
from configs.global_constants import HAZ_CLASSES
from operator import attrgetter
from configs.definitions import FCL_FREIGHT_CHARGES


def get_fcl_freight_rate(request):
  details = {}

  if request['rate_type'] == 'cogo_assured':
    object=find_cogo_assured_rate(request)
    return object
  else:
    del request['id']
    del request['rate_type']

  if all_fields_present(request):
    object = find_object(request)
    fcl_object = object
    if object:
      details = object.detail()
  else:
    fcl_object=None

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

  if not fcl_object:
    fcl_object = FclFreightRate()
    for key in list(request.keys()):
      setattr(fcl_object, key, request[key])
  fcl_object.set_locations()
  return details | ({
    'freight_charge_codes': (fcl_object.possible_charge_codes()),
    'origin_local_charge_codes': (FclFreightRateLocal(**origin_local_object_params).possible_charge_codes()),
    'destination_local_charge_codes': (FclFreightRateLocal(**destination_local_object_params).possible_charge_codes())
  })


def find_object(object_params):
  query = FclFreightRate.select()
  for key in object_params:
    query = query.where(attrgetter(key)(FclFreightRate) == object_params[key])
  # print(query.first())
  object = query.first()
  
  return object

def all_fields_present(object_params):
  if ((object_params['origin_port_id'] is not None) and (object_params['destination_port_id'] is not None) and (object_params['container_size'] is not None) and (object_params['container_type'] is not None) and (object_params['shipping_line_id'] is not None) and (object_params['service_provider_id'] is not None)) :
    return True
  return False
def remove_empty_values(request):
    return  dict(filter(lambda item: item[1], request.items()))

def find_cogo_assured_rate(object_params):
  try:
    object = FclFreightRate.select().where(FclFreightRate.id==object_params['id']).dicts().get()
  except:
    clean_request = remove_empty_values(object_params)
    object = find_object(clean_request)
    # print(object)
    return model_to_dict(object)
  return object
  