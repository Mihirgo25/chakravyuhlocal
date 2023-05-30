from services.fcl_customs_rate.models.fcl_customs_rate import FclCustomsRate
from services.fcl_customs_rate.models.fcl_customs_rate_audit import FclCustomsRateAudit
from fastapi import HTTPException
from database.db_session import db


def update_fcl_customs_rate(request):
    with db.atomic():
        return execute_transaction_code(request)
    
def execute_transaction_code(request):
    rate_object = find_rate_object(request)
    if not rate_object:
        raise HTTPException(status_code=500, detail='Rate Not Found')
    
    rate_object.customs_line_items = request.get('customs_line_items')
    rate_object.cfs_line_items = request.get('cfs_line_items')
    rate_object.procured_by_id = request.get('procured_by_id')
    rate_object.sourced_by_id = request.get('sourced_by_id')
    
    rate_object.set_platform_price
    rate_object.set_is_best_price

    try:
        rate_object.save()
    except Exception as e:
        print("Exception in updating rate", e)

    rate_object.update_customs_line_item_messages

    rate_object.update_cfs_line_item_messages

    create_audit_for_updating_rate(request, rate_object)

    rate_object.update_platform_prices_for_other_service_providers

    return {'id': rate_object.id}

def find_rate_object(request):
    try:
        rate_object = FclCustomsRate.get_by_id(request['id'])
    except:
        rate_object = None
    return rate_object

def create_audit_for_updating_rate(request, rate_object):
    data = {key:value for key, value in request.items() if key not in ['performed_by_id', 'id', 'bulk_operation_id']}
    
    FclCustomsRateAudit.create(
      action_name =  'update',
      performed_by_id =  request.get('performed_by_id'),
      bulk_operation_id =  request.get('bulk_operation_id'),
      object_id = rate_object.id,
      object_type = 'FclCustomsRate',
      data = data
    )