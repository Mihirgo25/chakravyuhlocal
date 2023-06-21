from services.air_customs_rate.models.air_customs_rate import AirCustomsRate
from micro_services.client import organization

def find_service_providers(request):
    data = {
        'airport_id': request.get('airport_id'),
        'country_id': request.get('country_id')
    }
    if request.get('commodity'):
        data['commodity'] = request.get('commodity')

    ids = organization.get_eligible_service_organizations({
      'service': 'air_customs',
      'data': data
    })['ids']

    return ids

def create_air_customs_rate_not_available(request):
    service_provider_query = AirCustomsRate.select(AirCustomsRate.service_provider_id).distinct().where(
      AirCustomsRate.airport_id == request.get('airport_id'),
      AirCustomsRate.trade_type == request.get('trade_type'),
      AirCustomsRate.commodity == request.get('commodity'),
      AirCustomsRate.importer_exporter_id == None
    ).dicts()

    present_service_provider_ids = []
    for id in service_provider_query:
        present_service_provider_ids.append(id.get('service_provider_id'))

    find_service_provider_ids = find_service_providers(request)
    
    for service_provider_id in list(set(find_service_provider_ids).difference(set(present_service_provider_ids))):
        AirCustomsRate.create(
            airport_id = request['airport_id'],
            trade_type = request['trade_type'],
            commodity = request['commodity'],
            service_provider_id = service_provider_id,
            rate_not_available_entry = True
        )

    return True