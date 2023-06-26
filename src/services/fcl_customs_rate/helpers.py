from services.fcl_customs_rate.models.fcl_customs_rate import FclCustomsRate
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE
from micro_services.client import organization
from database.db_session import rd
from libs.parse_numeric import parse_numeric

def update_organization_fcl_customs(request):
    query = FclCustomsRate.select(
                FclCustomsRate.id
            ).where(
                FclCustomsRate.service_provider_id == request.get("service_provider_id"), 
                FclCustomsRate.rate_not_available_entry == False, 
                FclCustomsRate.rate_type == DEFAULT_RATE_TYPE).exists()

    if not query:
        params = {
            "id" : request.get("service_provider_id"), 
            "freight_rates_added" : True
        }
        organization.update_organization(params)

processed_percent_hash = "process_percent_customs_bulk_operation"

def processed_percent_key(id):
    return f"fcl_customs_rate_bulk_operation_{id}"

def set_processed_percent_customs_bulk_operation(processed_percent, id):
    if rd:
        rd.hset(processed_percent_hash, processed_percent_key(id), processed_percent)