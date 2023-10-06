from services.ftl_freight_rate.models.ftl_freight_rate import FtlFreightRate
from services.ftl_freight_rate.interactions.list_ftl_freight_rates import list_ftl_freight_rates
from micro_services.client import maps, shipment
from datetime import datetime
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from fastapi.encoders import jsonable_encoder
import json

BATCH_SIZE = 500

def get_ftl_freight_rate_min_max_validity_dates(request): 
    ftl_freight_min_max_dates = get_ftl_freight_validity_dates_in_batches(request)
    flash_booking_min_max_dates = get_flash_booking_validity_dates_in_batches(request)
    
    min_validity_end_dates = list(filter(None, [ftl_freight_min_max_dates['min_validity_end_date'],
                                               flash_booking_min_max_dates['min_validity_end_date']]))
    max_validity_end_dates = list(filter(None, [ftl_freight_min_max_dates['max_validity_end_date'],
                                               flash_booking_min_max_dates['max_validity_end_date']]))

    min_validity_end_date = (min(min_validity_end_dates) if len(min_validity_end_dates)>0 else None)
    max_validity_end_date = (max(max_validity_end_dates) if len(max_validity_end_dates)>0 else None)

    return {'min_validity_end_date': min_validity_end_date,
            'max_validity_end_date': max_validity_end_date}

def get_ftl_freight_validity_dates_in_batches(request):
    filters = get_ftl_freight_rate_params(request)
    ftl_freight_rate = list_ftl_freight_rates(filters= filters, return_query= True, page_limit= MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT)['list']
    ftl_freight_date_count = len(ftl_freight_rate)
    result = {'min_validity_end_date': None, 'max_validity_end_date': None}
    offset = 0
    
    while offset < ftl_freight_date_count:
        ftl_freight_batch_query = ftl_freight_rate.select(FtlFreightRate.validity_end).offset(offset).limit(BATCH_SIZE)
        ftl_freight_batch_data = list(ftl_freight_batch_query.dicts())
        result = get_result_from_batch(result, ftl_freight_batch_data)
        offset += BATCH_SIZE

    return result

def get_flash_booking_validity_dates_in_batches(request):
    flash_bookings_date_count = 1
    result = {'min_validity_end_date': None, 'max_validity_end_date': None}
    page = 1

    while flash_bookings_date_count>0:
        flash_booking_batch_data = shipment.list_shipment_flash_booking_rates({'filters':{'shipment_id':request['shipment_id'], 'preferred_currency':request['preferred_currency']}, 'page': page,'page_limit': BATCH_SIZE})['list']
        result = get_result_from_batch(result, flash_booking_batch_data)
        flash_bookings_date_count = len(flash_booking_batch_data)
        page += 1
        
    return result

def get_result_from_batch(result, batch_data):
    for row in batch_data:
        if row['validity_end'] != None:
            row['validity_end'] = str(row['validity_end'])[:10]
            result['min_validity_end_date'] = (min(result['min_validity_end_date'], row['validity_end'])
                                        if result['min_validity_end_date'] != None else row['validity_end'])
            result['max_validity_end_date'] = (max(result['max_validity_end_date'], row['validity_end'])
                                        if result['max_validity_end_date'] != None else row['validity_end'])
    return result

def get_ftl_freight_rate_params(request):
    
    ftl_freight_rate_params = {key: value for key, value in request.items() 
                               if (value != None) and (key not in ['shipment_id','preferred_currency'])}
    ftl_freight_rate_params['rate_not_available_entry'] = False
    ftl_freight_rate_params['is_line_items_error_messages_present'] = False

    origin_location_id = request.get('origin_location_id')
    destination_location_id = request.get('destination_location_id')

    if origin_location_id or destination_location_id:
        location_ids = [origin_location_id, destination_location_id]
        locations_response = maps.list_locations({'filters':{"id": location_ids}})
        locations = locations_response["list"] 
        city_ids = {}

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
 
    if request['trip_type'] == 'round':
        ftl_freight_rate_params['trip_type'] = 'round_trip'
    else:
        ftl_freight_rate_params['trip_type'] = 'one_way'
        
    ftl_freight_rate_params['validity_till'] = request.get('cargo_readiness_date') or datetime.now()
    
    return ftl_freight_rate_params



    



