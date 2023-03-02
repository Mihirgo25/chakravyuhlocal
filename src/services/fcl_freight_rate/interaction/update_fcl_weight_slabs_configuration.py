from database.db_session import db
from services.fcl_freight_rate.interaction.create_fcl_freight_rate import to_dict
from services.fcl_freight_rate.models.fcl_weight_slabs_configuration import FclWeightSlabsConfiguration
from libs.logger import logger 

def update_fcl_weight_slabs_configuration(request):
    with db.atomic() as transaction:
        try:
            data = execute_transaction_code(request)
            return data
        except:
            transaction.rollback()
            return 'Updation Failed'

def execute_transaction_code(request):
    updated_configuration = FclWeightSlabsConfiguration.get_by_id(request['id'])
    
    updation_params = {key:value for key,value in request if key != 'id'}
    for attr,value in updation_params.items():
        setattr(updated_configuration, attr, value)
    
    if not updated_configuration.save():
        logger.error(updated_configuration.errors)
        return
 
    return {
    'id': request['id']
    }