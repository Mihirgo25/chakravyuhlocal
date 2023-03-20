from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from playhouse.shortcuts import model_to_dict
from micro_services.client import organization

def create_fcl_freight_rate_not_available(request):
    request = request.__dict__
    present_service_provider_data = FclFreightRate.select(FclFreightRate.service_provider_id).distinct().where(
        FclFreightRate.origin_port_id == request['origin_port_id'],
        FclFreightRate.destination_port_id == request['destination_port_id'],
        FclFreightRate.container_size == request['container_size'],
        FclFreightRate.container_type == request['container_type'],
        FclFreightRate.commodity == request['commodity'],
        FclFreightRate.importer_exporter_id == None
    )
    present_service_provider_ids = [model_to_dict(item)['service_provider_id'] for item in present_service_provider_data.execute()]

    for service_provider_id in list(set(find_service_provider_ids(request)).difference(set(present_service_provider_ids))):
        FclFreightRate.create(
            origin_port_id = request['origin_port_id'],
            destination_port_id = request['destination_port_id'],
            container_size = request['container_size'],
            container_type = request['container_type'],
            commodity = request['commodity'],
            service_provider_id = service_provider_id,
            rate_not_available_entry = True)
    return True

def find_service_provider_ids(request):
    service_provider_ids = organization.get_eligible_service_organizations({
    'service': 'fcl_freight',
    'data': {
        'origin_port_id': request['origin_port_id'],
        'origin_country_id': request['origin_country_id'],
        'origin_trade_id': request['origin_trade_id'],
        'destination_port_id': request['destination_port_id'],
        'destination_country_id': request['destination_country_id'],
        'destination_trade_id': request['destination_trade_id'],
        'container_type': request['container_type'],
        'commodity': request['commodity']
    }
    })['ids']

    return service_provider_ids