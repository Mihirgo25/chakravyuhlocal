from services.ftl_freight_rate.models.ftl_freight_rate_bulk_operation import FtlFreightRateBulkOperation
from celery_worker import update_multiple_service_objects
from services.ftl_freight_rate.ftl_celery_worker import ftl_bulk_operation_perform_action_functions

def create_ftl_freight_rate_bulk_operation(request):
    action_name = [key for key in request if key not in ['performed_by_type', 'performed_by_id', 'service_provider_id', 'procured_by_id', 'sourced_by_id']][0]
    data = request[action_name]

    params = {'action_name':action_name,
              'data':data, 
              'performed_by_id':request.get('performed_by_id'), 
              'service_provider_id':request.get('service_provider_id'), 
              'sourced_by_id':request['sourced_by_id'], 
              'procured_by_id':request['procured_by_id']
              }
    bulk_operation = FtlFreightRateBulkOperation(**params)
    eval(f"bulk_operation.validate_{action_name}_data()")

    bulk_operation.save()
    
    ftl_bulk_operation_perform_action_functions.apply_async(
        kwargs={
            'action_name':action_name,
            'object':bulk_operation, 
            'sourced_by_id':request["sourced_by_id"],
            'procured_by_id':request['procured_by_id']
            },queue='low')
    
    return {
    'id': str(bulk_operation.id)
    }