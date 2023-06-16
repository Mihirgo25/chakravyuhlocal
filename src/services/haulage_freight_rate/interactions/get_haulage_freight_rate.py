
from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
from operator import attrgetter

def all_fields_present(requirements):
    if all(key in requirements for key in ('origin_location_id', 'destination_location_id', 'container_size', 'container_type', 'haulage_type', 'transport_modes', 'service_provider_id')):
        return True

def find_object(requirement):
    object = HaulageFreightRate.select().where(attrgetter(get_object_params(requirement))(HaulageFreightRate))
    return object

def get_object_params(requirement):
    return {
      'origin_location_id': requirement.get('origin_location_id'),
      'destination_location_id': requirement.get('destination_location_id'),
      'container_size': requirement.get('container_size'),
      'container_type': requirement.get('container_type'),
      'commodity': requirement.get('commodity'),
      'transit_time': requirement.get('transit_time'),
      'detention_free_time': requirement.get('detention_free_time'),
      'trip_type': requirement.get('trip_type'),
      'trailer_type': requirement.get('trailer_type'),
      'haulage_type': requirement.get('haulage_type'),
      'transport_modes_keyword': requirement.get('transport_modes'),
      'service_provider_id': requirement.get('service_provider_id'),
      'importer_exporter_id': requirement.get('importer_exporter_id'),
      'shipping_line_id': requirement.get('shipping_line_id')
    }

def get_haulage_freight_rate(requirement):
    """
    Get the haulage freight rate for a given requirement.
    """

    if not all_fields_present(requirement):
        return {}
    
    object = find_object(requirement)
    get_data = list(object.dicts())[0]
    if get_data.get('detail'):
        detail = get_data['detail']
    else:
        detail = {}
    return detail
