from services.fcl_customs_rate.models.fcl_customs_rate import FclCustomsRate
from micro_services.client import organization
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE

def find_service_providers(request):
    ids = organization.get_eligible_service_organizations({
      'service': 'fcl_customs',
      'data': {
        'location_id': request.get('location_id'),
        'country_id': request.get('country_id'),
        'trade_type': request.get('trade_type'),
        'container_size': request.get('container_size'),
        'container_type': request.get('container_type'),
        'commodity': request.get('commodity')
      }
    })['ids']

    return ids

def create_fcl_customs_rate_not_available(request):
    service_provider_query = FclCustomsRate.select(FclCustomsRate.service_provider_id).distinct().where(
      FclCustomsRate.location_id == request.get('location_id'),
      FclCustomsRate.trade_type == request.get('trade_type'),
      FclCustomsRate.container_size == request.get('container_size'),
      FclCustomsRate.container_type == request.get('container_type'),
      FclCustomsRate.commodity == request.get('commodity'),
      FclCustomsRate.rate_type == DEFAULT_RATE_TYPE,
      FclCustomsRate.importer_exporter_id == None
    ).dicts()

    present_service_provider_ids = []
    for id in service_provider_query:
        present_service_provider_ids.append(id['service_provider_id'])

    find_service_provider_ids = find_service_providers(request)
    
    for service_provider_id in list(set(find_service_provider_ids).difference(set(present_service_provider_ids))):
        FclCustomsRate.create(
            location_id = request['location_id'],
            trade_type = request['trade_type'],
            container_size = request['container_size'],
            container_type = request['container_type'],
            commodity = request['commodity'],
            service_provider_id = service_provider_id,
            rate_not_available_entry = True,
            customs_line_items = [],
            cfs_line_items = [])

    return True