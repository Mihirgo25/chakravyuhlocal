from peewee import *
from services.fcl_cfs_rate.models.fcl_cfs_rate import FclCfsRate
from services.fcl_cfs_rate.models.fcl_cfs_rate_audit import FclCfsRateAudit
from celery_worker import delay_fcl_cfs_functions
from database.db_session import db
from fastapi import HTTPException

def create_audit_for_cfs_rate(request, cfs_object_id):
    audit_data = {
        "line_items": request.get("cfs_line_items"),
        "free_days": request.get("free_days")
    }
    
    FclCfsRateAudit.create(
        action_name = 'create',
        object_id = cfs_object_id,
        object_type = 'FclCfsRate',
        performed_by_id = request.get("performed_by_id"),
        rate_sheet_id = request.get('rate_sheet_id'),
        data = audit_data        
    )    

def create_fcl_cfs_rates(request):
    with db.atomic():
        return execute_transaction_code(request)
    
def execute_transaction_code(request):
    params = {
        "location_id": request.get("location_id"),
        "trade_type": request.get("trade_type"),
        "container_size": request.get("container_size"),
        "container_type": request.get("container_type"),
        "commodity": request.get("commodity"),
        "service_provider_id": request.get("service_provider_id"),
        "cargo_handling_type": request.get("cargo_handling_type"),
        "importer_exporter_id": request.get("importer_exporter_id")
    }

    cfs_object = FclCfsRate.select().where(
        FclCfsRate.location_id == request.get("location_id"),
        FclCfsRate.trade_type == request.get("trade_type"),
        FclCfsRate.container_size == request.get("container_size"),
        FclCfsRate.container_type == request.get("container_type"),
        FclCfsRate.commodity == request.get("commodity"), 
        FclCfsRate.service_provider_id == request.get("service_provider_id"), 
        FclCfsRate.cargo_handling_type == request.get("cargo_handling_type"),
        FclCfsRate.importer_exporter_id == request.get("importer_exporter_id")).first()

    if not cfs_object:
        cfs_object = FclCfsRate(**params)
        cfs_object.set_location()

    cfs_object.line_items = request.get('line_items')
    cfs_object.free_days = request.get('free_days')
    cfs_object.rate_not_available_entry = False
    cfs_object.set_platform_price()
    cfs_object.set_is_best_price()
    cfs_object.validate_mandatory_free_days()

    cfs_object.sourced_by_id = request.get("sourced_by_id")
    cfs_object.procured_by_id = request.get("procured_by_id")

    if not request["importer_exporter_id"]:
        cfs_object.delete_rate_not_available_entry()

    cfs_object.update_line_item_messages()
    cfs_object.validate_before_save()

    try:
        cfs_object.save()
    except Exception as e:
      raise HTTPException(status_code=500, detail='Customs Rate did not save')

    create_audit_for_cfs_rate(request, cfs_object.id)
    
    cfs_object.update_platform_prices_for_other_service_providers()
    delay_fcl_cfs_functions.apply_async(kwargs={'fcl_cfs_object':cfs_object,'request':request},queue='low')
    
    return {
      "id": cfs_object.id
    }