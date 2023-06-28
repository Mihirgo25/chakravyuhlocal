from services.fcl_cfs_rate.models.fcl_cfs_rate import *
from services.fcl_cfs_rate.models.fcl_cfs_rate_audit import FclCfsRateAudit
from fastapi import HTTPException
from datetime import datetime

def delete_fcl_cfs_rate(request):
        with db.atomic():
            return execute_transaction_code(request)

def execute_transaction_code(request):
    object = find_object(request.get('id'))

    if not object:
        raise HTTPException(status_code=400, detail="Rate not found")
    if not request.get('procured_by_id') or not request.get('sourced_by_id'):
        raise HTTPException(status_code=400, detail="procured or sourced by is Empty")

    delete_params = get_delete_params_for_cfs(request)
    for field, value in delete_params.items():
        setattr(object, field, value)

    try:
        object.save()
    except Exception as e:
        print("Exception in saving freight rate", e)

    create_audit_for_cfs_delete(request, object)

    return {'id': object.id}

def find_object(id):
    try:
        object = FclCfsRate.select().where(FclCfsRate.id == id).first()
    except:
        object = None
    return object

def get_delete_params_for_cfs(request):
    return {
        'line_items': [],
        'free_days': [],
        'rate_not_available_entry': True,
        'platform_price': None,
        'is_best_price': None,
        'is_line_items_error_messages_present': None,
        'is_line_items_info_messages_present': None,
        'line_items_error_messages': None,
        'line_items_info_messages': None,
        'procured_by_id': request.get('procured_by_id'),
        'sourced_by_id':request.get('sourced_by_id'),
        'updated_at': datetime.now().isoformat()
    }

def create_audit_for_cfs_delete(request, object):
    data = get_delete_params_for_cfs(request)
    FclCfsRateAudit.create(
        action_name = 'delete',
        bulk_operation_id = request.get('bulk_operation_id'),
        object_id = object.id,
        performed_by_id = request.get('performed_by_id'),
        data = data,
        object_type = 'FclCfsRate'
    )