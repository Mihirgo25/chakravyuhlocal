from peewee import *
from services.fcl_cfs_rate.models.fcl_cfs_rate import FclCfsRate
from services.fcl_cfs_rate.models.fcl_cfs_rate_audit import FclCfsRateAudit
from fastapi import HTTPException
from database.db_session import db

def create_audit_for_updating_cfs(request, cfs_object_id):
    audit_data = {
        "line_items": request.get('line_items')
    }

    FclCfsRateAudit.create(
        action_name = 'update',
        object_id = cfs_object_id,
        object_type = 'FclCfsRate',
        performed_by_id = request.get("performed_by_id"),
        bulk_operation_id = request.get("bulk_operation_id"),
        data = audit_data
    )

def update_fcl_cfs_rate(request):
    with db.atomic():
        return execute_transaction_code(request)
    
def execute_transaction_code(request):
    cfs_object = find_cfs_object(request)

    if not cfs_object:
        raise HTTPException(status_code=500, detail='Rate Not Found')
    
    update_params =  {
        'procured_by_id':request.get('procured_by_id'),
        'sourced_by_id':request.get('sourced_by_id'),
        'line_items':request.get('line_items'),
        'free_limit':request.get('free_limit')
    }

    for key in list(update_params.keys()):
        setattr(cfs_object, key, update_params[key])

    cfs_object.set_platform_price()
    cfs_object.set_is_best_price()
    cfs_object.update_line_item_messages()
    
    create_audit_for_updating_cfs(request, cfs_object.id)
    
    cfs_object.update_platform_prices_for_other_service_providers()
    
    try:
        cfs_object.save()
    except Exception as e:
        print("Exception in updating rate", e)

    return {'id': cfs_object.id}

def find_cfs_object(request):
    try:
        cfs_object = FclCfsRate.get_by_id(request.get("id"))
    except:
        cfs_object = None
    
    return cfs_object