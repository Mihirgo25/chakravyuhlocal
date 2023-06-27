from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
from playhouse.shortcuts import model_to_dict
from micro_services.client import organization



def create_haulage_freight_rate_not_available(request):
    request = request.__dict__
    transport_modes = request.get('transport_modes',[])
    transport_modes = set(transport_modes)
    transport_modes = list(transport_modes)
    transport_modes.sort()
    present_service_provider_data = HaulageFreightRate.select(HaulageFreightRate.service_provider_id).distinct().where(
        HaulageFreightRate.origin_location_id == request['origin_location_id'],
        HaulageFreightRate.destination_location_id == request['destination_location_id'],
        HaulageFreightRate.container_size == request['container_size'],
        HaulageFreightRate.container_type == request['container_type'],
        HaulageFreightRate.commodity == request['commodity'],
        HaulageFreightRate.haulage_type == request['haulage_type'],
        HaulageFreightRate.shipping_line_id == request['shipping_line_id'],
        HaulageFreightRate.importer_exporter_id == None,
        HaulageFreightRate.transport_modes_keyword == '_'.join(transport_modes)

    )

    present_service_provider_ids = [model_to_dict(item)['service_provider_id'] for item in present_service_provider_data.execute()]

    for service_provider_id in list(set(find_service_provider_ids(request)).difference(set(present_service_provider_ids))):
        HaulageFreightRate.create(
            origin_location_id = request.get('origin_location_id'),
            destination_location_id = request.get('destination_location_id'),
            container_size = request.get('container_size'),
            container_type = request.get('container_type'),
            commodity = request.get('commodity'),
            haulage_type = request.get('haulage_type'),
            service_provider_id = service_provider_id,
            shipping_line_id = request.get('shipping_line_id'),
            transport_modes = request.get('transport_modes'),
        )

    return True

def find_service_provider_ids(request):
    service_provider_ids = organization.get_eligible_service_organizations({
    'service': 'haulage_freight',
    'data': {
        'origin_location_id': request.get('origin_location_id'),
        'origin_country_id': request.get('origin_country_id'),
        'destination_location_id': request.get('destination_location_id'),
        'destination_country_id': request.get('destination_country_id'),
        'container_size': request.get('container_size'),
        'container_type': request.get('container_type'),
        'commodity': request.get('commodity'),
        'transport_modes': request.get('transport_modes')
    }
    })['ids']

    return service_provider_ids

