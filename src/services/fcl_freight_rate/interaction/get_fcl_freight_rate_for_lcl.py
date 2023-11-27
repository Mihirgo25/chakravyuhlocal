from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from operator import attrgetter
from services.envision.interaction.get_fcl_freight_predicted_rate import get_fcl_freight_predicted_rate
from services.chakravyuh.interaction.get_serviceable_shipping_lines import get_serviceable_shipping_lines
import datetime
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE

def get_fcl_freight_rate_for_lcl(request):
  details = []
  source = 'fcl_freight_rate'
  
  if all_fields_present(request):
    fcl_objects = find_object(request)
    for fcl_object in fcl_objects:
        details.append(fcl_object.detail() | ({
    'freight_charge_codes': (fcl_object.possible_charge_codes())
  }))
        fcl_object.set_locations()
    
    if not details:
        request['is_source_lcl'] = True
        serviceable_shipping_lines = get_serviceable_shipping_lines(request)
        details  = get_fcl_freight_predicted_rate(request, serviceable_shipping_lines)
        for detail in details:
            detail['freight'] = {'validities':[]}
            detail['freight']['validities'].append(
            {'line_items': detail['line_items'],
            'validity_start': detail['validity_start'],
            'validity_end': detail['validity_end']}
            )
            del detail['line_items']
            del detail['validity_start']
            del detail['validity_end']
        source = 'predicted'
      
  return {'details': details,'source': source}


def find_object(object_params):
  query = FclFreightRate.select().where(FclFreightRate.last_rate_available_date >= datetime.datetime.now(), FclFreightRate.rate_type == DEFAULT_RATE_TYPE)
  for key in object_params:
      if object_params[key]:
        query = query.where(attrgetter(key)(FclFreightRate) == object_params[key])
  return query

def all_fields_present(object_params):
  if (object_params['origin_port_id'] is not None) and (object_params['destination_port_id'] is not None) and (object_params['container_size'] is not None) and (object_params['container_type'] is not None):
    return True
  return False