from services.fcl_freight_rate.models.fcl_weight_slabs_configuration import FclWeightSlabsConfiguration
from database.db_session import db
from fastapi import HTTPException

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
        FclWeightSlabsConfiguration.origin_location_id == request.get('origin_location_id'),
        FclWeightSlabsConfiguration.origin_location_type == request.get('origin_location_type'),
        FclWeightSlabsConfiguration.destination_location_id == request.get('destination_location_id'),
        FclWeightSlabsConfiguration.destination_location_type == request.get('destination_location_type'),
        FclWeightSlabsConfiguration.container_size == request.get('container_size'),
        FclWeightSlabsConfiguration.organization_category == request.get('organization_category'),
        FclWeightSlabsConfiguration.shipping_line_id == request.get('shipping_line_id'),
        FclWeightSlabsConfiguration.service_provider_id == request.get('service_provider_id'),
        FclWeightSlabsConfiguration.importer_exporter_id == request.get('importer_exporter_id'),
        FclWeightSlabsConfiguration.is_cogo_assured == request.get('is_cogo_assured'),
        FclWeightSlabsConfiguration.commodity == request.get('commodity'),
        FclWeightSlabsConfiguration.max_weight == request.get('max_weight'),
        FclWeightSlabsConfiguration.trade_type == request.get('trade_type')
    )

    new_configuration = new_configuration.first()
    if not new_configuration:
        new_configuration = FclWeightSlabsConfiguration(**params)

    for key, value in request.items(): 
        setattr(new_configuration, key, value) 

    new_configuration.price = request['slabs'][0].get('price')
    new_configuration.currency = request['slabs'][0].get('currency')

    if request['origin_location_id']:
        if not request['origin_location_type']:
            raise HTTPException(status_code= 400, detail = 'origin_location_type cannot be blank')
        elif not request['destination_location_id']:
            raise HTTPException(status_code = 400, detail = 'destination_location_id cannot be blank')
              
    if request['destination_location_id']:
        if not request['destination_location_type']:
            raise HTTPException(status_code= 400, detail = 'destination_location_type cannot be blank') 
        elif not request['origin_location_id']:
            raise HTTPException(status_code= 400, detail = 'origin_location_id cannot be blank')
    
    new_configuration.status = 'active'

    if new_configuration.validate():
        new_configuration.save()

    return {'id' : new_configuration.id}