from database.db_session import db
from fastapi import HTTPException
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
    object = AirFreightStorageRate.select().where(
        AirFreightStorageRate.airport_id == request.get('airport_id'),
        AirFreightStorageRate.airline_id == request.get('airline_id'),
        AirFreightStorageRate.trade_type == request.get('trade_type'),
        AirFreightStorageRate.commodity == request.get('commodity'),
        AirFreightStorageRate.service_provider_id == request.get('service_provider_id')
    ).first()

    if not object:
        object = AirFreightStorageRate(**row)

    object.slabs = request.get('slabs')
    object.remarks = request.get('remarks')
    object.free_limit = request.get('free_limit')

    try:
        object.save()
    except:
        raise HTTPException(status_code = 404,details = 'Error in Saving Object')
    
