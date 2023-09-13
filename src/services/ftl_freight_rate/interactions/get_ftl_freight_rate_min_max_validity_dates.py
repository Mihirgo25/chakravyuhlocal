from services.ftl_freight_rate.models.ftl_freight_rate import FtlFreightRate
from services.ftl_freight_rate.interactions.list_ftl_freight_rates import list_ftl_freight_rates
from micro_services.client import maps
from datetime import datetime
from database.rails_db import list_shipment_flash_booking_rates
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from fastapi.encoders import jsonable_encoder
import json

BATCH_SIZE = 500

def get_ftl_freight_rate_min_max_validity_dates(request): 
    response = perform_bulk_operation(request)
    return response

def perform_bulk_operation(request):
    
    filters = get_ftl_freight_rate_params(request)
    page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
    result = {'min_validity_end_date' : None, 'max_validity_end_date' : None}

    ftl_freight_rate = list_ftl_freight_rates(filters= filters, return_query= True, page_limit= page_limit)['list']
    validity_end_date_count = len(ftl_freight_rate)
    offset = 0

    while offset < validity_end_date_count:
        ftl_freight_batch_query = ftl_freight_rate.select(FtlFreightRate.validity_end).offset(offset).limit(BATCH_SIZE)
        ftl_freight_batch_data = list(ftl_freight_batch_query.dicts())
        result = get_result_from_batch(result, ftl_freight_batch_data)
        offset += BATCH_SIZE
    
    validity_end_date_count = 1
    offset = 0

    while validity_end_date_count>0:
        flash_booking_batch_data = list_shipment_flash_booking_rates(request['shipment_id'], request['preferred_currency'], offset, BATCH_SIZE)
        validity_end_date_count = len(flash_booking_batch_data)
        result = get_result_from_batch(result, flash_booking_batch_data)
        offset += BATCH_SIZE

    return result

def get_result_from_batch(result, batch_data):
    for row in batch_data:
            if row['validity_end'] != None:
                row['validity_end'] = str(row['validity_end'])
                result['min_validity_end_date'] = (min(result['min_validity_end_date'], row['validity_end'])
                                         if result['min_validity_end_date'] != None else row['validity_end'])
                result['max_validity_end_date'] = (max(result['max_validity_end_date'], row['validity_end'])
                                         if result['max_validity_end_date'] != None else row['validity_end'])
    
    return result

def get_ftl_freight_rate_params(request):
    ftl_freight_rate_params = {
        'importer_exporter_id': request.get('importer_exporter_id'),
        'rate_not_available_entry': False,
        'is_line_items_error_messages_present': False
    }
    
    if request.get('truck_type'):
        truck_type = request.get('truck_type')
        truck_type = json.loads(truck_type)
        ftl_freight_rate_params['truck_type'] = truck_type
    if request.get('commodity'):
        ftl_freight_rate_params['commodity'] = request.get('commodity')

    origin_location_id = request.get('origin_location_id')
    destination_location_id = request.get('destination_location_id')
    
    if origin_location_id or destination_location_id:
        ids = list(filter(None,[str(origin_location_id), str(destination_location_id)]))
        locations_response = maps.list_locations({'filters':{"id": ids}})
        city_ids = {}
        locations = []

        if 'list' in locations_response:
                locations = locations_response["list"] 
        for location in locations:
            if str(location['id']) == str(origin_location_id):
                city_ids['origin_city_id'] = location.get("city_id")
            elif str(location['id']) == str(destination_location_id):
                city_ids['destination_city_id'] = location.get("city_id")

        origin_location_ids = list(filter(None, [origin_location_id, city_ids.get('origin_city_id')]))
        destination_location_ids = list(filter(None, [destination_location_id, city_ids.get('destination_city_id')]))

        if origin_location_ids:
            ftl_freight_rate_params['origin_location_id'] = origin_location_ids
        if destination_location_ids:
            ftl_freight_rate_params['destination_location_id'] = destination_location_ids

    ftl_freight_rate_params['trip_type'] = "round_trip" if 'round' in request['trip_type'] else 'one_way'
    ftl_freight_rate_params['validity_till'] = request.get('cargo_readiness_date') or datetime.now()
    
    return ftl_freight_rate_params



    



