from peewee import *
from services.fcl_cfs_rate.models.fcl_cfs_rate import FclCfsRate
from playhouse.shortcuts import model_to_dict
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE
from database.rails_db import get_eligible_orgs   
        

def find_service_provider_ids():
    service_provider_ids = get_eligible_orgs('fcl_cfs')
    return service_provider_ids

def create_fcl_cfs_rate_not_available(request):
    present_service_provider_data = FclCfsRate.select(
         FclCfsRate.service_provider_id
         ).distinct(
        ).where(
            FclCfsRate.location_id == request["location_id"], 
            FclCfsRate.trade_type == request["trade_type"], 
            FclCfsRate.container_size == request["container_size"],
            FclCfsRate.container_type == request["container_type"],
            FclCfsRate.commodity == request["commodity"],
            FclCfsRate.rate_type == DEFAULT_RATE_TYPE,
            FclCfsRate.importer_exporter_id.is_null(True))

    present_service_provider_ids = [model_to_dict(item).get('service_provider_id') for item in present_service_provider_data.execute()]
    missing_service_provider_ids = list(set(find_service_provider_ids()).difference(set(present_service_provider_ids)))

    for service_provider_id in missing_service_provider_ids:
        FclCfsRate.create(
            location_id=request["location_id"],
            trade_type=request["trade_type"],
            container_size=request["container_size"],
            container_type=request["container_type"],
            commodity=request["commodity"],
            service_provider_id=service_provider_id,
            rate_not_available_entry=True,
            line_items=[]
        )

    return True