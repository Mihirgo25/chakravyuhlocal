from services.ftl_freight_rate.models.ftl_freight_rate_bulk_operation import FtlFreightRateBulkOperation
from database.db_session import db
from services.ftl_freight_rate.ftl_celery_worker import bulk_operation_perform_action_functions
from fastapi import HTTPException


def create_ftl_freight_rate_bulk_operation(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    action_name = [key for key in request if key not in ['performed_by_type', 'performed_by_id', 'service_provider_id', 'procured_by_id', 'sourced_by_id']][0]
    data = request[action_name]

    params = {
        'action_name':action_name,
        'data':data,
        'performed_by_id':request.get('performed_by_id'),
        'service_provider_id':request.get('service_provider_id'),
        'sourced_by_id':request['sourced_by_id'],
        'procured_by_id':request['procured_by_id']
    }
    try:
        bulk_operation_object = FtlFreightRateBulkOperation(**params)
        eval(f"bulk_operation_object.validate_{action_name}_data()")
        bulk_operation_object.save(force_insert=True)
    except Exception as error_message:
        raise HTTPException(status_code=500, detail="error_message")
    
    bulk_operation_perform_action_functions.apply_async(
        kwargs={
            'action_name':action_name,
            'object':bulk_operation_object, 
            'sourced_by_id':request["sourced_by_id"],
            'procured_by_id':request['procured_by_id']
        },
        queue='bulk_operations'
    )
    
    return {
    'id': str(bulk_operation_object.id)
    }