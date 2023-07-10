
from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
from operator import attrgetter

default_fields = [ 'line_items',
        'transit_time',
        'detention_free_time',
        'trip_type',
        'validity_start',
        'validity_end',
        'trailer_type',
        'line_items_info_messages',
        'is_line_items_info_messages_present',
        'line_items_error_messages',
        'is_line_items_error_messages_present']

def all_fields_present(requirements):
    if all(requirements.get(key) for key in ('origin_location_id', 'destination_location_id', 'container_size', 'container_type', 'haulage_type', 'transport_modes', 'service_provider_id')):
        return True

def find_object(requirement):
    fields = [getattr(HaulageFreightRate, key) for key in default_fields]
    query = HaulageFreightRate.select(*fields)
    object_params= get_object_params(requirement)
    for key in object_params:
      if object_params[key]:
        query = query.where(attrgetter(key)(HaulageFreightRate) == object_params[key])
    return query

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
    Response Format:
        key value pair of details of that specific rate
    """
    
    if not all_fields_present(requirement):
        return {}
    
    object = find_object(requirement)
    detail = {"Rate": "Rate not found"}
    if object:
        detail = list(object.dicts())[0]
        object_params= get_object_params(requirement)
        object_params['transport_modes'] = requirement['transport_modes']
        object = HaulageFreightRate(**object_params)
        object.set_origin_location_ids
        object.set_destination_location_ids
        object.possible_charge_codes
        detail['haulage_freight_charge_codes'] = object.__data__

    return detail
