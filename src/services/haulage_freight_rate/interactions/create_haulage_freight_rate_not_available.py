from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
from database.rails_db import get_eligible_orgs
from fastapi.encoders import jsonable_encoder


def create_haulage_freight_rate_not_available(request):
    """
    Create Haulage Rate Not Available
    Response Format:
        {"id": created_rate_ids}
    """

    transport_modes = request.get('transport_modes',[])
    transport_modes = list(set(transport_modes))
    transport_modes.sort()
    transport_modes = '_'.join(transport_modes)
    present_service_provider_data = HaulageFreightRate.select(HaulageFreightRate.service_provider_id).distinct().where(
        HaulageFreightRate.origin_location_id == request['origin_location_id'],
        HaulageFreightRate.destination_location_id == request['destination_location_id'],
        HaulageFreightRate.container_size == request['container_size'],
        HaulageFreightRate.container_type == request['container_type'],
        HaulageFreightRate.commodity == request['commodity'],
        HaulageFreightRate.haulage_type == request['haulage_type'],
        HaulageFreightRate.shipping_line_id == request['shipping_line_id'],
        HaulageFreightRate.importer_exporter_id == None,
        HaulageFreightRate.transport_modes_keyword == transport_modes
    )
    present_service_provider_ids = [ids['service_provider_id'] for ids in jsonable_encoder(list(present_service_provider_data.dicts()))]
    
    find_service_provider_ids = find_service_providers()

    created_rate_ids = []

    for service_provider_id in list(set(find_service_provider_ids).difference(set(present_service_provider_ids))):
        object = HaulageFreightRate.create(
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
        created_rate_ids.append(object.id)

    return created_rate_ids

def find_service_providers():
    service_provider_ids = get_eligible_orgs('haulage_freight')
    return service_provider_ids

