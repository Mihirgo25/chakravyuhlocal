from services.fcl_cfs_rate.models.fcl_cfs_rate import FclCfsRate
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE
from micro_services.client import organization
from database.db_session import rd

def update_organization_fcl_cfs(request):
    query = FclCfsRate.select(
                FclCfsRate.id
            ).where(
                FclCfsRate.service_provider_id == request.get("service_provider_id"), 
                FclCfsRate.rate_not_available_entry == False, 
                FclCfsRate.rate_type == DEFAULT_RATE_TYPE).exists()

    if not query:
        params = {
            "id" : request.get("service_provider_id"), 
            "freight_rates_added" : True
        }
        organization.update_organization(params)

def processed_percent_key(id):
    return f"fcl_cfs_rate_bulk_operation_{id}"

def set_processed_percent_cfs_bulk_operation(processed_percent, id):
    processed_percent_hash = "process_percent_cfs_bulk_operation"
    if rd:
        rd.hset(processed_percent_hash, processed_percent_key(id), processed_percent)