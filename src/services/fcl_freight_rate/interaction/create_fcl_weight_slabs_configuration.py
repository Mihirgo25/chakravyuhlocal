from services.fcl_freight_rate.models.fcl_weight_slabs_configuration import FclWeightSlabsConfiguration
from database.db_session import db

def create_fcl_weight_slabs_configuration(request):
    with db.atomic() as transaction:
        try:
            return execute_transaction_code(request)
        except Exception as e:
            transaction.rollback()
            return e

def execute_transaction_code(request):
    params = {key:value for key,value in request.items() if key != 'slabs'}
    params['status'] = 'active'

    new_configuration = FclWeightSlabsConfiguration.select().where(
        FclWeightSlabsConfiguration.origin_location_id == request.get('origin_location_id') if request.get('origin_location_id') else FclWeightSlabsConfiguration.id.is_null(False),
        FclWeightSlabsConfiguration.origin_location_type == request.get('origin_location_type') if request.get('origin_location_type') else FclWeightSlabsConfiguration.id.is_null(False),
        FclWeightSlabsConfiguration.destination_location_id == request.get('destination_location_id') if request.get('destination_location_id') else FclWeightSlabsConfiguration.id.is_null(False),
        FclWeightSlabsConfiguration.destination_location_type == request.get('destination_location_type') if request.get('destination_location_type') else FclWeightSlabsConfiguration.id.is_null(False),
        FclWeightSlabsConfiguration.container_size == request.get('container_size') if request.get('container_size') else FclWeightSlabsConfiguration.id.is_null(False),
        FclWeightSlabsConfiguration.organization_category == request.get('organization_category') if request.get('organization_category') else FclWeightSlabsConfiguration.id.is_null(False),
        FclWeightSlabsConfiguration.shipping_line_id == request.get('shipping_line_id') if request.get('shipping_line_id') else FclWeightSlabsConfiguration.id.is_null(False),
        FclWeightSlabsConfiguration.service_provider_id == request.get('service_provider_id') if request.get('service_provider_id') else FclWeightSlabsConfiguration.id.is_null(False),
        FclWeightSlabsConfiguration.importer_exporter_id == request.get('importer_exporter_id') if request.get('importer_exporter_id') else FclWeightSlabsConfiguration.id.is_null(False),
        FclWeightSlabsConfiguration.is_cogo_assured == request.get('is_cogo_assured') if request.get('is_cogo_assured') else FclWeightSlabsConfiguration.id.is_null(False),
        FclWeightSlabsConfiguration.commodity == request.get('commodity') if request.get('commodity') else FclWeightSlabsConfiguration.id.is_null(False),
        FclWeightSlabsConfiguration.max_weight == request.get('max_weight'),
        FclWeightSlabsConfiguration.trade_type == request.get('trade_type') if request.get('trade_type') else FclWeightSlabsConfiguration.id.is_null(False)
    ).first()

    if not new_configuration:
        new_configuration = FclWeightSlabsConfiguration(**params)

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