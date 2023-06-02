from services.fcl_cfs_rate.models.fcl_cfs_rate import FclCfsRate
from peewee import *
from configs.fcl_cfs_rate_constants import FREE_DAYS_TYPES
from operator import attrgetter

def get_fcl_cfs_rate(request):
    if all(value for key, value in request.items() if key not in ['importer_exporter_id','commodity']):
        try:
            fcl_cfs_rate = get_cfs_object(request)
            detail = fcl_cfs_rate.detail()

        except DoesNotExist:
            fcl_cfs_rate = FclCfsRate(**request)
            detail = {}

        response = {
            'detail': detail,
            'fcl_cfs_charge_codes': fcl_cfs_rate.possible_charge_codes(),
            'fcl_cfs_free_days': FREE_DAYS_TYPES
        }
    else:
        response = {}

    return response

def get_cfs_object(request):
  query = FclCfsRate.select()
  for key in request:
    query = query.where(attrgetter(key)(FclCfsRate) == request[key])
  object = query.first()
  
  return object


        
    
          
