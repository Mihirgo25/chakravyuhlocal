from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from playhouse.shortcuts import model_to_dict
from database.rails_db import get_eligible_orgs


def create_air_freight_rate_not_available(request):
    present_service_provider_query = AirFreightRate.select(AirFreightRate.service_provider_id).distinct().where(
        AirFreightRate.origin_airport_id==request.get('origin_airport_id'),
        AirFreightRate.destination_airport_id == request.get('destination_airport_id'),
        AirFreightRate.commodity == request.get('commodity')
    )
    present_service_provider_ids = [model_to_dict(item)['service_provider_id'] for item in present_service_provider_query.execute()]

    for service_provider_id in list(set(present_service_provider_ids)-set(find_service_providers())):
        AirFreightRate.create(
            origin_airport_id = request['origin_airport_id'],
            destination_airport_id = request['destination_airport_id'],
            commodity = request['commodity'],
            service_provider_id = service_provider_id,
            rate_not_available_entry = True
        )
    return True

def find_service_providers():
    service_provider_ids = get_eligible_orgs('air_freight')
    return service_provider_ids
