from datetime import datetime
from fastapi import HTTPException
from database.db_session import db 
from services.air_freight_rate.models.air_freight_warehouse_rate import AirFreightWarehouseRates
from services.air_freight_rate.models.air_services_audit import AirServiceAudit
from celery_worker import update_multiple_service_objects

def create_air_freight_warehouse_rate(request):
    object_type = 'Air_Freight_Warehouse_Rate' 
    query = "create table if not exists air_services_audits_{} partition of air_services_audits for values in ('{}')".format(object_type.lower(), object_type.replace("_","")) 
    db.execute_sql(query)
    with db.atomic():
        return execute_transaction_code(request)
    
def execute_transaction_code(request):
    row={
        'airport_id':request.get('airport_id'),
        'trade_type':request.get('trade_type'),
        'commodity':request.get('commodity'),
        'service_provider_id':request.get('service_provider_id')
    }
    object=AirFreightWarehouseRates.select().where(AirFreightWarehouseRates.id==request.get('id'))

    if not object:
        object=AirFreightWarehouseRates(**row)
        object.update_freight_object()

    object.line_items=request.get('line_items')
    object.procured_by_id=request.get('procured_by_id')
    object.sourced_by_id=request.get('sourced_by_id')

    object.update_line_item_messages()

    object.delete_rate_not_available_entry()

    update_multiple_service_objects.apply_async(kwargs={'object':object},queue='low')

    if object.validate():
        try:
            object.save()
        except:
            raise HTTPException(status_code=400,detail='save couldnt be done')
        
    create_audit(request,object)
    
    return{
        'id':str(object.id)
    }

def create_audit(request,object):
    AirServiceAudit.create(
        data=request.get('line_items'),
        action_name='create',
        performed_by_id=request.get('performed_by_id'),
        rate_sheet_id=request.get('rate_sheet_id'),
        bulk_operation_id=request.get('bulk_operation_id'),
        object_type='AirFreightWarehouseRate',
        object_id=object.id
    )
