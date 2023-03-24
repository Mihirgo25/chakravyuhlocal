from services.fcl_freight_rate.models.fcl_freight_rate_bulk_operation import FclFreightRateBulkOperation
from celery_worker import bulk_operation_perform_action_functions,update_multiple_service_objects

def create_fcl_freight_rate_bulk_operation(request):
    action_name = [key for key in request if key not in ['performed_by_id', 'service_provider_id', 'procured_by_id', 'sourced_by_id', 'cogo_entity_id']][0]
    data = request[action_name]
    
    params = {'action_name':action_name, 'data':data, 'performed_by_id':request['performed_by_id'], 'service_provider_id':request['service_provider_id'],'sourced_by_id':request['sourced_by_id'],'procured_by_id':request['procured_by_id']}
    bulk_operation = FclFreightRateBulkOperation(**params)
    eval(f"bulk_operation.validate_{action_name}_data()")

    bulk_operation.save()
    update_multiple_service_objects.apply_async(kwargs={'object':bulk_operation},queue='low')

    bulk_operation_perform_action_functions.apply_async(kwargs={'action_name':action_name,
    'object':bulk_operation,'sourced_by_id':request["sourced_by_id"],
    'procured_by_id':request['procured_by_id'],'cogo_entity_id':request.get('cogo_entity_id')},queue='low')
    return {
    'id': str(bulk_operation.id)
    }