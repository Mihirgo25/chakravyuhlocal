from services.fcl_cfs_rate.models.fcl_cfs_rate import FclCfsRate,possible_charge_codes
from playhouse.shortcuts import model_to_dict
from peewee import *
from configs.fcl_cfs_rate_constants import FREE_DAYS_TYPES

def get_fcl_cfs_rate(request):
    if all(value for value in request.values()):
        try:
            fcl_cfs_rate = FclCfsRate.get(**request)
            detail = fcl_cfs_rate.detail
        except DoesNotExist:
            detail = {}
        response = {
            'detail': detail,
            'fcl_cfs_charge_codes': fcl_cfs_rate.possible_charge_codes(),
            'fcl_cfs_free_days': FREE_DAYS_TYPES
        }
    else:
        response = {}

    return response
        
    
          
