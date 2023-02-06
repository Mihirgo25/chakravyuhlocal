from services.fcl_freight_rate.models.fcl_freight_rates import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_locals import FclFreightRateLocals
from configs.global_constants import HAZ_CLASSES
from services.fcl_freight_rate.models.fcl_freight_rates import possible_charge_codes
import json 

# def to_dict(obj):
#     return json.loads(json.dumps(obj, default=lambda o: o.__dict__))

def get_fcl_freight_rate(request):
  detail = {}

  object_params = {
    'origin_port_id': request.origin_port_id,
    'origin_main_port_id': request.origin_main_port_id,
    'destination_port_id': request.destination_port_id,
    'destination_main_port_id': request.destination_main_port_id,
    'container_size': request.container_size,
    'container_type': request.container_type,
    'commodity': request.commodity,
    'shipping_line_id': request.shipping_line_id,
    'service_provider_id': request.service_provider_id,
    'importer_exporter_id': request.importer_exporter_id
  }

  if (request.origin_port_id) & (request.destination_port_id) & (request.container_size) & (request.container_type) & (request.shipping_line_id) & (request.service_provider_id):
    object = find_object(object_params)

    if object:
      detail = object.detail
    
  origin_local_object_params = {
    'port_id': request.origin_port_id,
    'main_port_id': request.origin_main_port_id,
    'trade_type': 'export',
    'container_size': request.container_size,
    'container_type': request.container_type,
    'shipping_line_id': request.shipping_line_id,
    'service_provider_id': request.service_provider_id
    }

  destination_local_object_params = {
    'port_id': request.origin_port_id,
    'main_port_id': request.origin_main_port_id,
    'trade_type': 'export',
    'container_size': request.container_size,
    'container_type': request.container_type,
    'shipping_line_id': request.shipping_line_id,
    'service_provider_id': request.service_provider_id
    }
  
  if request.commodity in HAZ_CLASSES:
    origin_local_object_params['commodity'] = request.commodity
    destination_local_object_params['commodity'] = request.commodity
  else:
    origin_local_object_params['commodity'] = None
    destination_local_object_params['commodity'] = None


  return detail.update({
    'freight_charge_codes': possible_charge_codes(FclFreightRate.get(object_params)),
    'origin_local_charge_codes': possible_charge_codes(FclFreightRateLocals.get(origin_local_object_params)),
    'destination_local_charge_codes': possible_charge_codes(FclFreightRateLocals.get(destination_local_object_params))
  })


def find_object(object_params):
  object = FclFreightRate.where(**object_params).eager_load('port_origin_local', 'port_destination_local').limit(1).dicts()

  return object

