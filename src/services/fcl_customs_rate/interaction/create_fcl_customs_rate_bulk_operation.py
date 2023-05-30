from services.fcl_customs_rate.models.fcl_customs_rate_bulk_operation import FclCustomsRateBulkOperation

def create_fcl_customs_rate_bulk_operation(request):
    # from celery_worker import update_multiple_service_objects, bulk_operation_perform_action_functions

    action_name = [key for key in request if key not in ['performed_by_id', 'service_provider_id', 'procured_by_id', 'sourced_by_id','cogo_entity_id']]
    if action_name:
        action_name = action_name[0]

        data = request[action_name]
        
        params = get_bulk_operation_params(request, action_name, data)
        bulk_operation_customs = FclCustomsRateBulkOperation(**params)
        eval(f"bulk_operation_customs.validate_{action_name}_data()")

        # update_multiple_service_objects.apply_async(kwargs={'object':bulk_operation_customs},queue='low')

        bulk_operation_customs.save()
        if action_name == 'add_markup':
            bulk_operation_customs.perform_add_markup_action(request.get('procured_by_id'), request.get("sourced_by_id"))

        if action_name == 'delete_rate':
            bulk_operation_customs.perform_delete_rate_action(request.get('procured_by_id'), request.get("sourced_by_id"))

        # bulk_operation_perform_action_functions.apply_async(kwargs={'action_name':action_name,
        # 'object':bulk_operation_customs,'sourced_by_id':request.get("sourced_by_id"),
        # 'procured_by_id':request.get('procured_by_id'),'cogo_entity_id':request.get('cogo_entity_id')},queue='low')
        
        return {
        'id': bulk_operation_customs.id
        }

def get_bulk_operation_params(request, action_name, data):
    return {
        'action_name':action_name, 
        'data':data, 
        'performed_by_id':request.get('performed_by_id'), 
        'service_provider_id':request.get('service_provider_id')
    }