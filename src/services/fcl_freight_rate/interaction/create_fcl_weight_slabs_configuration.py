from services.fcl_freight_rate.models.fcl_weight_slabs_configuration import FclWeightSlabsConfiguration
from database.db_session import db
from services.fcl_freight_rate.helpers.find_or_initialize import find_or_initialize
from libs.logger import logger
from fastapi import HTTPException

def create_fcl_weight_slabs_configuration(request):
    with db.atomic() as transaction:
        try:
            return execute_transaction_code(request)
        except Exception as e:
            logger.error(e, exc_info=True)
            transaction.rollback()
            return e

def execute_transaction_code(request):
    params = {key:value for key,value in request.items() if key != 'slabs'}
    params['status'] = 'active'

    new_configuration = find_or_initialize(FclWeightSlabsConfiguration, **params)
    for key, value in request.items(): 
        setattr(new_configuration, key, value) 

    if request['origin_location_id']:
        if not request['origin_location_type']:
            raise Exception('origin_location_type cannot be blank')
        elif not request['destination_location_id']:
            raise Exception('destination_location_id cannot be blank')
              
    if request['destination_location_id']:
        if not request['destination_location_type']:
            raise Exception('destination_location_type cannot be blank') 
        elif not request['origin_location_id']:
            raise Exception('origin_location_id cannot be blank')
    
    new_configuration.status = 'active'

    if new_configuration.validate():
        new_configuration.save()

    return new_configuration.id