from services.fcl_freight_rate.models.fcl_freight_rate_weight_limit import FclFreightRateWeightLimit
from operator import attrgetter


def find_or_initialize(**kwargs):
  try:
    print('do')
    obj = FclFreightRateWeightLimit.get(**kwargs)
  except FclFreightRateWeightLimit.DoesNotExist:
    print('doesnt')
    obj = FclFreightRateWeightLimit(**kwargs)
  return obj

def get_weight_limit_object(request):
    row = {
      'origin_location_id': request['origin_location_id'],
      'destination_location_id': request['destination_location_id'],
      'container_size': request['container_size'],
      'container_type': request['container_type'],
      'shipping_line_id': request['shipping_line_id'],
      'service_provider_id': request['service_provider_id']
    }
    weight_limit = find_or_initialize(**row)
    print('weight_limit', weight_limit)

    extra_fields = ['free_limit','remarks','slabs']
    for field in extra_fields:
       if field in request:
          var = attrgetter(field)(weight_limit) #remove var
          if var:
             if var != request[field]:
              print('var1', var)
              setattr(weight_limit, field, request[field])
              print('var2', var)
          else:
             print('var3', var)
             setattr(weight_limit, field, request[field])
             print('var4', var)

    return weight_limit

def create_fcl_freight_rate_weight_limit(request):
  weight_limit = get_weight_limit_object(request)
  print('weight_limit_3', weight_limit)

  weight_limit.save()
  print('weight_limit', weight_limit)
  return