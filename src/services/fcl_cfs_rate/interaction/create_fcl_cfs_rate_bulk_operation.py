from peewee import *
from services.fcl_cfs_rate.models.fcl_cfs_rate_bulk_operation import FclCfsRateBulkOperation
from celery_worker import update_multiple_service_objects, bulk_operation_perform_action_functions_customs_cfs

def get_bulk_operation_params(request, action_name, data):
    params = {
        'action_name':action_name, 
        'data':data, 
        'performed_by_id':request.get('performed_by_id'), 
        'service_provider_id':request.get('service_provider_id'),
        "sourced_by_id":request.get('sourced_by_id'),
        "procured_by_id":request.get('procured_by_id')
    }
    return params


def create_fcl_cfs_rate_bulk_operation(request):
    action_name = [key for key in request if key not in ['performed_by_type','performed_by_id', 'service_provider_id', 'procured_by_id', 'sourced_by_id']]

    if action_name:
        action_name=action_name[0]

        data = request[action_name]

        params = get_bulk_operation_params(request, action_name, data)
        bulk_operation = FclCfsRateBulkOperation.create(**params)

        eval(f"bulk_operation.validate_{action_name}_data()")

        bulk_operation.save()

        bulk_operation_perform_action_functions_customs_cfs.apply_async(kwargs={'action_name':action_name,
        'object':bulk_operation,'sourced_by_id':request.get("sourced_by_id"),
        'procured_by_id':request.get('procured_by_id')},queue='low')
        
        return {
            'id': bulk_operation.id
        }
