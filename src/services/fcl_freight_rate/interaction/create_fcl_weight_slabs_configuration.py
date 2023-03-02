from services.fcl_freight_rate.models.fcl_weight_slabs_configuration import FclWeightSlabsConfiguration
from database.db_session import db
from datetime import datetime

def create_fcl_weight_slabs_configuration(request):
    with db.session() as transaction:
        try:
            return execute_transaction_code(request)
        except:
            transaction.rollback()
            return 'Creation Failed'

def execute_transaction_code(request):
    params = {key:value for key,value in request if key != 'slabs'}
    params = get_params(params)
    new_configuration = find_or_initialize(**params)
    for key, value in new_configuration.items(): 
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

    new_configuration.save()

    return new_configuration.id


def get_params(params):
    optional_parameters = ['origin_location_id', 'destination_location_id', 'origin_location_type', 'destination_location_type', 'organization_category', 'shipping_line_id', 'service_provider_id', 'importer_exporter_id', 'is_cogo_assured' , 'container_size', 'commodity', 'trade_type']
    for optional_parameter in optional_parameters:
        if not params[optional_parameter]:
            params[optional_parameter] = None 
    
    params['status'] = 'active'
    return params

def find_or_initialize(**kwargs):
  try:
    obj = FclWeightSlabsConfiguration.get(**kwargs)
    obj.updated_at = datetime.now()
  except FclWeightSlabsConfiguration.DoesNotExist:
    obj = FclWeightSlabsConfiguration(**kwargs)
  return obj