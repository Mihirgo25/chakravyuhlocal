from services.fcl_customs_rate.models.fcl_customs_rate import FclCustomsRate
from services.fcl_customs_rate.models.fcl_customs_rate_audit import FclCustomsRateAudit
from database.db_session import db  
from fastapi import HTTPException

def delete_fcl_customs_rate(request):
    with db.atomic():
        return execute_transaction_code(request)
    
def execute_transaction_code(request):
    rate_object = find_rate_object(request)
    if not rate_object:
        raise HTTPException(status_code=500, detail='Rate Not Found')
    
    delete_params = get_params_for_deletion()

    for key in list(delete_params.keys()):
        setattr(rate_object, key, delete_params[key])

    rate_object.procured_by_id = request.get('procured_by_id')
    rate_object.sourced_by_id = request.get('sourced_by_id')

    try:
        rate_object.save()
    except Exception as e:
         print("Exception in deleting rate", e)

    rate_object.update_platform_prices_for_other_service_providers

    create_audit_for_delete_rates(request, rate_object, delete_params)

    return {
      'id': rate_object.id
    }

def find_rate_object(request):
    try:
        rate_object = FclCustomsRate.get_by_id(request['id'])
    except:
        rate_object = None
    return rate_object

def create_audit_for_delete_rates(request, rate_object, delete_params):
    FclCustomsRateAudit.create(
        action_name = 'delete',
        performed_by_id = request.get('performed_by_id'),
        bulk_operation_id = request.get('bulk_operation_id'),
        object_id = rate_object.id,
        object_type = 'FclCustomsRate',
        data = delete_params
    )

def get_params_for_deletion():
    return {
      'customs_line_items': [],
      'cfs_line_items': [],
      'rate_not_available_entry': True,
      'platform_price': None,
      'is_best_price': None,
      'is_customs_line_items_error_messages_present': None,
      'is_customs_line_items_info_messages_present': None,
      'customs_line_items_error_messages': None,
      'customs_line_items_info_messages': None,
      'is_cfs_line_items_error_messages_present': None,
      'is_cfs_line_items_info_messages_present': None,
      'cfs_line_items_error_messages': None,
      'cfs_line_items_info_messages': None
    }