from peewee import *
from services.fcl_cfs_rate.models.fcl_cfs_rate import FclCfsRate
from services.fcl_cfs_rate.models.fcl_cfs_audits import FclCfsRateAudits
from services.fcl_cfs_rate.interaction.update_fcl_cfs_rate_platform_prices import update_platform_prices_for_other_service_providers
from celery_worker import delay_fcl_functions

def get_audit_params(request):
    audit_data = {
        "line_items": request.line_items,
        "free_days": request.free_days
        }

    return {
        "action_name": 'create',
        "performed_by_id": request["performed_by_id"],
        "sourced_by_id": request["sourced_by_id"],
        "procured_by_id": request["procured_by_id"],
        "rate_sheet_id": request["rate_sheet_id"],
        "data": audit_data
    }
    

def create_fcl_cfs_rates(request):
    params = {
        "rate_sheet_id": request["rate_sheet_id"],
        "location_id": request["location_id"],
        "trade_type": request["trade_type"],
        "container_size": request["container_size"],
        "container_type": request["container_type"],
        "commodity": request["commodity"],
        "service_provider_id": request["service_provider_id"],
        "performed_by_id": request["performed_by_id"],
        "sourced_by_id": request["sourced_by_id"],
        "procured_by_id": request["procured_by_id"],
        "cargo_handling_type": request["cargo_handling_type"],
        "importer_exporter_id": request["importer_exporter_id"],
        "line_items": request["line_items"],
        "free_days": request["free_days"]
    }

    freight = FclCfsRate.select().where(
        (FclCfsRate.location_id == request["location_id"]),
        (FclCfsRate.trade_type == request["trade_type"]),
        (FclCfsRate.container_size == request["container_size"]),
        (FclCfsRate.container_type == request["container_type"]),
        (FclCfsRate.commodity == request["commodity"]), 
        (FclCfsRate.service_provider_id == request["service_provider_id"]), 
        (FclCfsRate.cargo_handling_type == request["cargo_handling_type"]),
        (FclCfsRate.importer_exporter_id == request["importer_exporter_id"])).execute()

    if not freight:
        freight = FclCfsRate.create(**params)

    
    if request["importer_exporter_id"] is None or request["importer_exporter_id"]=='':
        FclCfsRate.delete_rate_not_available_entry()
        
    FclCfsRate.update_line_item_messages()

    audit_params = get_audit_params(request)
    FclCfsRateAudits.create(**audit_params)

    update_platform_prices_for_other_service_providers(request)

    delay_fcl_functions.apply_async(kwargs={'fcl_object':freight,'request':request},queue='low')
    
    return {
      "id": freight.id
    }