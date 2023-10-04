from services.fcl_customs_rate.models.fcl_customs_rate import FclCustomsRate
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE
from micro_services.client import organization

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
            "customs_rates_added" : True
        }
        organization.update_organization(params)