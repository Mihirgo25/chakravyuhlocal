from services.air_customs_rate.models.air_customs_rate import AirCustomsRate
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE
from micro_services.client import organization

def update_organization_air_customs(request):
    query = AirCustomsRate.select(
                AirCustomsRate.id
            ).where(
                AirCustomsRate.service_provider_id == request.get("service_provider_id"), 
                AirCustomsRate.rate_not_available_entry == False, 
                AirCustomsRate.rate_type == DEFAULT_RATE_TYPE).exists()

    if not query:
        params = {
            "id" : request.get("service_provider_id"), 
            "freight_rates_added" : True
        }

        organization.update_organization(params)