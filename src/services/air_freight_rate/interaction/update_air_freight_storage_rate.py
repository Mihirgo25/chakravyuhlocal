from fastapi import HTTPException
from database.db_session import db 
from services.air_freight_rate.models.air_freight_storage_rate import AirFreightStorageRates
from services.air_freight_rate.models.air_freight_rate_audit import AirFreightRateAudits


def update_air_freight_storage_rate(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    object = AirFreightStorageRates.select().where(AirFreightStorageRates.id==request['id']).first()

    if not object:
        raise HTTPException(status_code=400, detail='invalid id ')
    
    AirFreightStorageRates.update(
        slabs=request.get('slabs'),
        remarks=request.get('remarks')
    )
    
    object.update_special_attributes()

    create_audit(request,object.id)

    return {
        'id':str(object.id)
    }
def create_audit(request,id):
    AirFreightRateAudits.create(
        action_name='update',
        object_type='AirFreightStorageRates',
        object_id=object.id,
        performed_by_id=request['performed_by_id'],
        bulk_operation_id=request['bulk_operation_id'],
        data={k:v for k , v in request.items() if k not in ['performed_by_id','bulk_operation_id','procured_by_id','sourced_by_id']}
    )
