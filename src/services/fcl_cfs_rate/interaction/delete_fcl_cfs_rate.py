from services.fcl_cfs_rate.models.fcl_cfs_rate import *
from services.fcl_cfs_rate.models.fcl_cfs_audits import  FclCfsRateAudits
from fastapi import HTTPException
from uuid import UUID

def delete_fcl_cfs_rate(request):
        with db.atomic():
            return execute_transaction_code(request)

def execute_transaction_code(request):
    object = find_object(request['id'])
    if not object:
        raise HTTPException(status_code=400, detail="Rate not found")
    if request.get('procured_by_id') is None or request.get('sourced_by_id')is None:
        raise HTTPException(status_code=400, detail="procured or sourced by id is null")
    delete_params = get_delete_params_for_cfs(request)
    for field, value in delete_params.items():
            setattr(object, field, value)
    try:
        object.save()
    except Exception as e:
        print("Exception in saving freight rate", e)
    audit_params = get_audit_params_for_cfs_delete(request['performed_by_id'], request['bulk_operation_id'], delete_params)
    create_audit_for_cfs_delete(audit_params)

    return {'id': object.id}
def find_object(id):
    return FclCfsRate.get_or_none(id=id)

def get_delete_params_for_cfs(request):
    return {
        'cfs_line_items': [],
        'free_days': [],
        'rate_not_available_entry': True,
        'platform_price': None,
        'is_best_price': None,
        'is_cfs_line_items_error_messages_present': None,
        'is_cfs_line_items_info_messages_present': None,
        'cfs_line_items_error_messages': None,
        'cfs_line_items_info_messages': None,
        'procured_by_id': request.get('procured_by_id'),
        'sourced_by_id':request.get('sourced_by_id'),
        'updated_at':request.get('validity_start').strftime("%Y-%m-%d %H:%M:%S.%f")

    }

def get_audit_params_for_cfs_delete(performed_by_id, bulk_operation_id,delete_params):
    return {
        'action_name': 'delete',
        'performed_by_id': performed_by_id,
        'bulk_operation_id': bulk_operation_id,
        'data': delete_params
    }

def create_audit_for_cfs_delete(params):
    FclCfsRateAudits.create(**params)