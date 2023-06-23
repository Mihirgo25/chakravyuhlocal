from fastapi import HTTPException
from database.db_session import db 
from services.air_freight_rate.models.air_freight_warehouse_rate import AirFreightWarehouseRates
from services.air_freight_rate.models.air_services_audit import AirServiceAudit 

def update_air_freight_warehouse_rate(request):
    with db.atomic():
        return execute_transaction_code(request)
    
def execute_transaction_code(request):
    object=AirFreightWarehouseRates.select().where(AirFreightWarehouseRates.id==request['id']).first()
    if not object:
        raise HTTPException(status_code=400,detail="id is invalid")
    
    object.line_items=request['line_items']

    object.update_line_item_messages()
    try:
        object.save()
    except:
        raise HTTPException(status_code=400, detail='unable to save')
    
    create_audit(request,object)

    return {
        'id':object.id
    }
def create_audit(request,object):
    AirServiceAudit.create(
        data=request.get('line_items'),
        action_name='update',
        performed_by_id=request.get('performed_by_id'),
        object_type='AirFreightWarehouseRate',
        object_id=object.id
    )

