from services.ftl_freight_rate.models.ftl_freight_rate import FtlFreightRate
from services.ftl_freight_rate.interactions.list_ftl_freight_rates import list_ftl_freight_rates
from micro_services.client import maps
from datetime import datetime
from database.rails_db import list_shipment_flash_booking_rates
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from fastapi.encoders import jsonable_encoder

def get_ftl_freight_rate_min_max_validity_dates(request):
    ftl_frieght_rates = list_ftl_freight_rates(filters = get_ftl_freight_rate_params(request))['list']
    
    shipment_flash_booking_rates = list_shipment_flash_booking_rates(request['shipment_id'], request['preferred_currency'])
    
    ftl_validity_end_dates = [ row['validity_end'] for row in ftl_frieght_rates if row['validity_end'] != 'None']
    shipment_validity_end_dates = [ row['validity_end'] for row in shipment_flash_booking_rates if row['validity_end'] != 'None']
    
    all_validity_end_dates = (list(dict.fromkeys(filter(None, ftl_validity_end_dates + shipment_validity_end_dates))))
    breakpoint()
    return {
        'min_validity_end_date': min(all_validity_end_dates),
        'max_validity_end_date': max(all_validity_end_dates)
    }

def get_data(query):
    final_data = []
    data = jsonable_encoder(list(query.dicts()))

    for object in data:
        final_data.append(object)
    return final_data

def get_ftl_freight_rate_params(request):
    ftl_freight_rate_params = {
        'commodity': request.get('commodity'),
        'trip_type': request.get('trip_type'),
        'importer_exporter_id': request.get('importer_exporter_id'),
        'rate_not_available_entry': False,
        'is_line_items_error_messages_present': False
    }

    origin_location_id = request.get('origin_location_id')
    destination_location_id = request.get('destination_location_id')

    ids = [str(origin_location_id), str(destination_location_id)]
    locations_response = maps.list_locations({'filters':{"id": ids}})
    
    locations = []
    if 'list' in locations_response:
            locations = locations_response["list"]

    for location in locations:
        if str(location['id']) == str(origin_location_id):
            origin_city_id = location["city_id"]
        elif str(location['id']) == str(destination_location_id):
            destination_city_id = location["city_id"]
    
    ftl_freight_rate_params['trip_type'] = "round_trip" if 'round' in request['trip_type'] else 'one_way'

    ftl_freight_rate_params['origin_location_id'] = list(filter(None, [origin_location_id, origin_city_id]))
    ftl_freight_rate_params['destination_location_id'] = list(filter(None, [destination_location_id, destination_city_id]))

    ftl_freight_rate_params['validity_till'] = request.get('cargo_readiness_date') or datetime.now()
    
    return ftl_freight_rate_params



    



