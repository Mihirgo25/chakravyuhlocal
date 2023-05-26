from peewee import *
from services.fcl_cfs_rate.models.fcl_cfs_rate import FclCfsRate

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
        
    
    

    return True