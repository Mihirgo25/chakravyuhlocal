from services.air_customs_rate.models.air_customs_rate_bulk_operation import AirCustomsRateBulkOperation
from services.air_customs_rate.air_customs_celery_worker import bulk_operation_perform_action_functions_air_customs_delay

def create_air_customs_rate_bulk_operation(request):
    action_name = [key for key in request if key not in ['performed_by_id', 'service_provider_id', 'performed_by_type']]
    if action_name:
        action_name = action_name[0]

        data = request[action_name]

        params = get_air_bulk_operation_params(request, action_name, data)
        bulk_operation_customs_air = AirCustomsRateBulkOperation(**params)
        eval(f"bulk_operation_customs_air.validate_{action_name}_data()")

        bulk_operation_customs_air.save()
        bulk_operation_perform_action_functions_air_customs_delay.apply_async(
            kwargs={
                'action_name':action_name,
                'object':bulk_operation_customs_air
                },queue='low')

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