from database.db_session import db 
from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
from fastapi import HTTPException
from datetime import *
from services.air_freight_rate.models.air_services_audit import AirServiceAudit
# import sel,up

def update_air_freight_rate_local(request):
    object_type = 'Air_Freight_Rate_local' 
    query = "create table if not exists air_services_audits_{} partition of air_services_audits for values in ('{}')".format(object_type.lower(), object_type.replace("_","")) 
    db.execute_sql(query)
    with db.atomic():
        return execute_transaction_code(request)
    
def execute_transaction_code(request):
    
    air_freight_rate_local = AirFreightRateLocal.select().where(AirFreightRateLocal.id == request.get('id'))
    if not air_freight_rate_local:
        raise HTTPException(status_code=400, detail=" Surcharge not found")
    
    air_freight_rate_local.line_items=request.get('line_items')

    air_freight_rate_local.update_line_item_messages()
    
    try:
        air_freight_rate_local.save()
    except Exception:
        raise HTTPException(status_code=500, detail="Local rate not updated")

    create_audit(request)

    return {'id':str(air_freight_rate_local.id)}

def create_audit(request):
    
    data = {key:value for key,value in request.items() if key not in ['performed_by_id','bulk_operation_id','procured_by_id','sourced_by_id','id']}    
    AirServiceAudit.create(
        bulk_operation_id=request.get('bulk_operation_id'),
        action_name='update',
        data=data,
        object_id=request['id'],
        object_type='AirFreightRateLocal',
        performed_by_id=request.get('performed_by_id'),
        validity_id=request.get('validity_id')
    )
