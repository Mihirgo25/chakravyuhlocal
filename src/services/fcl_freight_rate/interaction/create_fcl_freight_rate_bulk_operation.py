from services.fcl_freight_rate.models.fcl_freight_rate_bulk_operation import FclFreightRateBulkOperation

def create_fcl_freight_rate_bulk_operation(request):
    action_name = [key for key in request if key not in ['performed_by_id', 'service_provider_id', 'procured_by_id', 'sourced_by_id', 'cogo_entity_id']][0]

    data = request[action_name]
    
    params = {'action_name':action_name, 'data':data, 'performed_by_id':request['performed_by_id'], 'service_provider_id':request['service_provider_id']}
    bulk_operation = FclFreightRateBulkOperation(**params)

    # bulk_operation.delay.eval(f"perform_{action_name}_action({request['sourced_by_id']},{request['procured_by_id']}, {request['cogo_entity_id']})")
    
    bulk_operation.save()
    
    return {
    'id': bulk_operation.id
    }