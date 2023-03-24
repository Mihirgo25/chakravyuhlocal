from database.db_session import db
from services.fcl_freight_rate.models.fcl_weight_slabs_configuration import FclWeightSlabsConfiguration
from libs.logger import logger 
from datetime import datetime

def update_fcl_weight_slabs_configuration(request):
    with db.atomic() as transaction:
        try:
            data = execute_transaction_code(request)
            return data
        except Exception as e:
            transaction.rollback()
            return e

def execute_transaction_code(request):
    request_id = request['id']
    del request['id']
    
    updated_configuration = FclWeightSlabsConfiguration.get(**{'id' : request_id})
        
    request['updated_at'] = datetime.now()
    request['price'] = request.get('slabs')[0].get('price')
    request['currency'] = request.get('slabs')[0].get('currency')
    
    for attr,value in request.items():
        setattr(updated_configuration, attr, value)

    if not updated_configuration.save():
        logger.error(updated_configuration.errors)
        return
 
    return {
    'id': request_id
    }