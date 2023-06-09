from services.air_customs_rate.models.air_customs_rate_bulk_operation import AirCustomsRateBulkOperation
from fastapi import HTTPException

def create_air_customs_rate_bulk_operation(request):
    from celery_worker import bulk_operation_perform_action_functions_customs_cfs

    action_name = [key for key in request if key not in ['performed_by_id', 'service_provider_id', 'procured_by_id', 'sourced_by_id', 'performed_by_type']]
    if action_name:
        action_name = action_name[0]

        data = request[action_name]
        
        params = get_air_bulk_operation_params(request, action_name, data)
        bulk_operation_customs_air = AirCustomsRateBulkOperation(**params)
        eval(f"bulk_operation_customs_air.validate_{action_name}_data()")
        
        try:
            bulk_operation_customs_air.save()
        except:
            raise HTTPException(status_code = 400, detail='Bulk Operation is not saved')

        bulk_operation_perform_action_functions_customs_cfs.apply_async(kwargs={'action_name':action_name,
        'object':bulk_operation_customs_air,'sourced_by_id':request.get("sourced_by_id"),
        'procured_by_id':request.get('procured_by_id')},queue='low')
        
        return {
        'id': bulk_operation_customs_air.id
        }

def get_air_bulk_operation_params(request, action_name, data):
    return {
        'action_name':action_name, 
        'data':data, 
        'performed_by_id':request.get('performed_by_id'), 
        'service_provider_id':request.get('service_provider_id')
    }