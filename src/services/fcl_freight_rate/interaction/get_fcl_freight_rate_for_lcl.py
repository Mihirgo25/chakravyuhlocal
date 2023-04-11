from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from operator import attrgetter
from services.envision.interaction.get_fcl_freight_predicted_rate import get_fcl_freight_predicted_rate

def get_fcl_freight_rate_for_lcl(request):
  details = []
  source = 'rates'
  
  if all_fields_present(request):
    fcl_objects = find_object(request)
    for fcl_object in fcl_objects:
        details.append(fcl_object.detail() | ({
    'freight_charge_codes': (fcl_object.possible_charge_codes())
  }))
        fcl_object.set_locations()
    
    if not details:
        details  = get_fcl_freight_predicted_rate(request)
        source = 'predicted'
      
  return {'details': details,'source': source}


def find_object(object_params):
  query = FclFreightRate.select()
  for key in object_params:
      if object_params[key]:
        query = query.where(attrgetter(key)(FclFreightRate) == object_params[key])
  return query

def all_fields_present(object_params):
  if (object_params['origin_port_id'] is not None) and (object_params['destination_port_id'] is not None) and (object_params['container_size'] is not None) and (object_params['container_type'] is not None):
    return True
  return False