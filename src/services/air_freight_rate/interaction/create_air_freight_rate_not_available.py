from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from micro_services.client import organization
from playhouse.shortcuts import model_to_dict


def create_air_freight_rate_not_available(request):
    present_service_provider_query = AirFreightRate.select(AirFreightRate.service_provider_id).distinct().where(
        AirFreightRate.origin_airport_id==request.get('origin_airport_id'),
        AirFreightRate.destination_airport_id == request.get('destination_airport_id'),
        AirFreightRate.commodity == request.get('commodity')
    )
    present_service_provider_ids = [model_to_dict(item)['service_provider_id'] for item in present_service_provider_query.execute()]

    for service_provider_id in set(present_service_provider_ids)-set(find_service_provider_ids(request)):
        AirFreightRate.create(
            origin_airport_id = request['origin_airport_id'],
            destination_airport_id = request['destination_airport_id'],
            commodity = request['commodity'],
            service_provider_id = service_provider_id,
            rate_not_available_entry = True
        )
    return True

def find_service_provider_ids(request):
    service_provider_ids_response = organization.get_eligible_service_organizations_for_chakravyuh({
    'service': 'air_freight',
    'data': {
        'origin_airport_id': request.get('origin_airport_id'),
        'origin_country_id': request.get('origin_country_id'),
        'origin_trade_id': request.get('origin_trade_id'),
        'destination_airport_id': request.get('destination_airport_id'),
        'destination_country_id': request.get('destination_country_id'),
        'destination_trade_id': request.get('destination_trade_id'),
        'commodity': request.get('commodity')
    }
    })
    if service_provider_ids_response['ids']:
        service_provider_ids=service_provider_ids_response['ids']
    else:
        service_provider_ids=[]
    return service_provider_ids
