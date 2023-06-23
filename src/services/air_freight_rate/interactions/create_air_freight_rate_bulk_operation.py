from datetime import datetime
from database.db_session import db  
from fastapi.encoders import jsonable_encoder
from services.air_freight_rate.models.air_freight_rate_bulk_operation import AirFreightRateBulkOperation 
from celery_worker import air_freight_bulk_operation_delay,update_multiple_service_objects



def create_air_freight_rate_bulk_operation(request):
    sourced_by_id=request.get("sourced_by_id")
    procured_by_id=request.get("procured_by_id")
    action_name=[key for key in request if key not in ['performed_by_type','performed_by_id', 'service_provider_id', 'procured_by_id', 'sourced_by_id', 'cogo_entity_id']][0]
    data=request[action_name] 
    params = {'action_name':action_name, 'data':data, 'performed_by_id':request.get('performed_by_id')}
    params =  jsonable_encoder(params)
    bulk_operation = AirFreightRateBulkOperation(**params)
    eval(f"bulk_operation.validate_{action_name}_data()")
    bulk_operation.save()
    
    update_multiple_service_objects.apply_async(kwargs={'object':bulk_operation},queue='low')

    air_freight_bulk_operation_delay.apply_async(kwargs={'action_name':action_name,'object':bulk_operation,'sourced_by_id':sourced_by_id,'procured_by_id':procured_by_id},queue='low')


    return {
    'id': str(bulk_operation.id)
    }

    