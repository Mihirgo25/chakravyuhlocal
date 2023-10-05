from services.air_customs_rate.models.air_customs_rate import AirCustomsRate
from database.rails_db import get_eligible_orgs
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE

def create_air_customs_rate_not_available(request):
    service_provider_query = AirCustomsRate.select(AirCustomsRate.service_provider_id).distinct().where(
      AirCustomsRate.airport_id == request.get('airport_id'),
      AirCustomsRate.trade_type == request.get('trade_type'),
      AirCustomsRate.commodity == request.get('commodity'),
      AirCustomsRate.rate_type == DEFAULT_RATE_TYPE,
      AirCustomsRate.importer_exporter_id == None
    ).dicts()

    present_service_provider_ids = []
    for id in service_provider_query:
        present_service_provider_ids.append(str(id.get('service_provider_id')))

    find_service_provider_ids = get_eligible_orgs(service = 'air_customs')

    for service_provider_id in list(set(find_service_provider_ids).difference(set(present_service_provider_ids))):
        AirCustomsRate.create(
            airport_id = request.get('airport_id'),
            country_id = request.get('country_id'),
            trade_type = request.get('trade_type'),
            commodity = request.get('commodity'),
            service_provider_id = service_provider_id,
            rate_not_available_entry = True
        )

    return True