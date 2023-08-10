from services.haulage_freight_rate.models.haulage_freight_rate_bulk_operation import HaulageFreightRateBulkOperation


def create_haulage_freight_rate_bulk_operation(request):
    """
    Create and delete Haulage Freight rate from a bulk operation
    Response Format:
        {"id": bulk_operation_id}
    """
    from services.haulage_freight_rate.haulage_celery_worker import bulk_operation_perform_action_functions_haulage
    from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
    request = {key: value for key, value in request.items() if value is not None}
    action_name = [key for key in request if key not in ['performed_by_type','performed_by_id', 'service_provider_id', 'procured_by_id', 'sourced_by_id']]
    if action_name:
        action_name=action_name[0]
        data = request[action_name]

        params = {'action_name':action_name,
                   'data':data, 
                   'performed_by_id':request.get('performed_by_id'), 
                   'service_provider_id':request['service_provider_id'],
                   'sourced_by_id':request['sourced_by_id'],
                   'procured_by_id':request['procured_by_id']}
        
        bulk_operation = HaulageFreightRateBulkOperation(**params)
        eval(f"bulk_operation.validate_{action_name}_data()")

        bulk_operation.save()
        get_multiple_service_objects(bulk_operation)

        bulk_operation_perform_action_functions_haulage.apply_async(
            kwargs={
                'action_name':action_name,
                'object':bulk_operation,
                'sourced_by_id':request["sourced_by_id"],
                'procured_by_id':request['procured_by_id']
            },queue='low')
        
        return {
            'id': str(bulk_operation.id)
        }
