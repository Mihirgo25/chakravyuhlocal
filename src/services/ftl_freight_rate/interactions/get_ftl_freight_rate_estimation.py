from services.ftl_freight_rate.interactions.create_ftl_freight_rate import create_ftl_freight_rate
from services.ftl_freight_rate.interactions.get_estimated_ftl_freight_rate import get_ftl_freight_rate
from micro_services.client import maps
from datetime import datetime,timedelta
from configs.ftl_freight_rate_constants import ENVISION_USER_ID, PREDICTED_PRICE_SERVICE_PROVIDER


def get_ftl_freight_rate_estimation(request):
    origin_location_id = request.get('origin_location_id')
    destination_location_id = request.get('destination_location_id')
    trip_type = request.get('trip_type')
    truck_type = request.get('truck_type')
    commodity = request.get('commodity')
    weight = request.get('weight')

    ftl_estimated_data = get_ftl_freight_rate(request)

    ftl_rates_list = ftl_estimated_data['list']
    try:
        ftl_freight_rate = ftl_rates_list[0]
    except:
        return False
    
    data = ftl_freight_rate 
    line_item = [
      {
        'code': 'BAS',
        'unit': 'per_truck',
        'price': data['base_price'],
        'currency': data['currency'],
        'remarks': []
      },
      {
        'code': 'FSC',
        'unit': 'per_truck',
        'price': 10,
        'currency': 'INR',
        'remarks': []
      }
    ]
    detention_free_time = 1
    transit_time = round((data['distance']//250)*24)
    if transit_time == 0:
        transit_time = 24
    
    validity_start = datetime.now().date().isoformat()
    validity_end = (datetime.now() + timedelta(days = 2)).date().isoformat()
    cogo_envision_id = ENVISION_USER_ID
    trip_type = 'round_trip' if 'round' in trip_type else trip_type

    params = {
        'origin_location_id': origin_location_id,
        'destination_location_id': destination_location_id,
        'trip_type': trip_type,
        'truck_type': data['truck_type'],
        'commodity': commodity,
        'service_provider_id': PREDICTED_PRICE_SERVICE_PROVIDER,
        'performed_by_id': cogo_envision_id,
        'procured_by_id': cogo_envision_id,
        'sourced_by_id': cogo_envision_id,
        'line_items': line_item,
        'truck_body_type': 'open' if 'open' in data['truck_type'] else 'closed',
        'transit_time': transit_time,
        'detention_free_time': detention_free_time,
        'validity_start': validity_start,
        'validity_end': validity_end,
        'minimum_chargeable_weight': 0 if truck_type is None else weight,
        'unit': 'per_truck' if truck_type else 'per_ton',
    }

    create_ftl_freight_rate(params)

    return ftl_estimated_data