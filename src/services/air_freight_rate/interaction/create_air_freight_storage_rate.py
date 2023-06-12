from database.db_session import db
from fastapi import HTTPException
from services.air_freight_rate.models.air_freight_storage_rate import AirFreightStorageRates
from services.air_freight_rate.models.air_freight_rate_audit import AirFreightRateAudits
from services.air_freight_rate.models.air_freight_storage_rate import AirFreightStorageRates 
def create_air_freight_storage_rate(request):
    with db.atomic():
        return execute_transaction_code(request)
    
def execute_transaction_code(request):

    row = {
        'airport_id' : request.get('airport_id'),
        'airline_id' : request.get('airline_id'),
        'trade_type' : request.get('trade_type'),
        'commodity'   :request.get('commodity'),
        'service_provider_id' : request.get('service_provider_id')
        }
    object = AirFreightStorageRates.select().where(
        AirFreightStorageRates.airport_id == request.get('airport_id'),
        AirFreightStorageRates.airline_id == request.get('airline_id'),
        AirFreightStorageRates.trade_type == request.get('trade_type'),
        AirFreightStorageRates.commodity == request.get('commodity'),
        AirFreightStorageRates.service_provider_id == request.get('service_provider_id')
    ).first()

    if not object:
        object = AirFreightStorageRates(**row)

    object.slabs = request.get('slabs')
    object.remarks = request.get('remarks')
    object.free_limit = request.get('free_limit')

    try:
        if object.validate():
            object.save()
    except:
        raise HTTPException(status_code = 404,detail = 'Error in Saving Object')
    
    create_audit(request,object)
    
    return {'id':object.id}

def create_audit(request,object):
    AirFreightRateAudits.create(
        action_name='create',
        object_type='AirFreightStorageRates',
        object_id=object.id,
        performed_by_id=request.get('performed_by_id'),
        bulk_operation_id=request.get('bulk_operation_id'),
        data={k:v for k , v in request.items() if k  in ['slabs','free_limit','remarks']}
    )
        
