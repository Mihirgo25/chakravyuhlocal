from services.trailer_freight_rate.interactions.get_estimated_trailer_freight_rate import get_estimated_trailer_freight_rate
from datetime import datetime,timedelta
from configs.haulage_freight_rate_constants import (ENVISION_USER_ID, 
                                                    PREDICTED_PRICE_SERVICE_PROVIDER,
                                                    PREDICTION_HAULAGE_TYPE, 
                                                    PREDICTION_TRAILER_TYPE, 
                                                    TRAILER_PREDICTION_TRANSPORT_MODES)
from configs.trailer_freight_rate_constants import DEFAULT_TRIP_TYPE
from services.haulage_freight_rate.interactions.create_haulage_freight_rate import create_haulage_freight_rate

def get_trailer_freight_rate_estimation(request):
    origin_location_id = request.get('origin_location_id')
    destination_location_id = request.get('destination_location_id')
    commodity = request.get('commodity')
    containers_count = request.get('containers_count')
    container_type = request.get('container_type')
    container_size = request.get('container_size')
    cargo_weight_per_container = request.get('cargo_weight_per_container')
    if not request.get('trip_type'):
        trip_type = DEFAULT_TRIP_TYPE

    req={"origin_location_id" : origin_location_id,
        "destination_location_id" : destination_location_id,
        "commodity" : commodity,
        "containers_count" : containers_count,
        "container_type" : container_type,
        "container_size" : container_size,
        "cargo_weight_per_container" : cargo_weight_per_container,
        "trip_type" : trip_type
        }
    

    trailer_estimated_data = get_estimated_trailer_freight_rate(req)
    list_data = trailer_estimated_data['list']
    data = list_data[0]
    line_item = [
        {
          "code": 'BAS',
          "unit": 'per_trailer',
          "price": data['base_price'],
          "currency": data['currency'],
          "remarks": [],
          "slabs": [
            {
              "price": data['base_price'],
              "lower_limit": 0,
              "upper_limit": data['upper_limit'],
              "currency": data['currency']
            }
          ]
        },
        {
          "code": 'FSC',
          "unit": 'per_trailer',
          "price": 10,
          "currency": 'INR',
          "remarks": [],
          "slabs": []
        }
      ]
    if not trailer_estimated_data:
        return False
    
    for data in trailer_estimated_data['list']:
        line_items = line_item
        detention_free_time = 1
        validity_start = datetime.now().date().isoformat()
        validity_end = (datetime.now() + timedelta(days = 60)).date().isoformat()
        cogo_envision_id = ENVISION_USER_ID

        params = {
            'origin_location_id': origin_location_id,
            'destination_location_id': destination_location_id,
            'container_size': container_size,
            'container_type': container_type,
            'service_provider_id': PREDICTED_PRICE_SERVICE_PROVIDER,
            'haulage_type': PREDICTION_HAULAGE_TYPE,
            'performed_by_id': cogo_envision_id,
            'procured_by_id': cogo_envision_id,
            'sourced_by_id': cogo_envision_id,
            'transport_modes': TRAILER_PREDICTION_TRANSPORT_MODES,
            'trailer_type': PREDICTION_TRAILER_TYPE,
            'line_items': line_items,
            'trip_type': trip_type,
            'transit_time': data.get('transit_time'),
            'detention_free_time': detention_free_time,
            'validity_start': validity_start,
            'validity_end': validity_end
        }

        create_haulage_freight_rate(params)
        
    return trailer_estimated_data