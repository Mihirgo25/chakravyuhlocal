
from services.haulage_freight_rate.interactions.get_estimated_haulage_freight_rate import haulage_rate_calculator
from datetime import datetime,timedelta
from configs.haulage_freight_rate_constants import (PREDICTED_PRICE_SERVICE_PROVIDER, 
                                                    PREDICTION_HAULAGE_TYPE, 
                                                    HAULAGE_PREDICTION_TRANSPORT_MODES)
from configs.env import DEFAULT_USER_ID
from services.haulage_freight_rate.interactions.create_haulage_freight_rate import create_haulage_freight_rate

def get_haulage_freight_rate_estimation(request):

    origin_location_id = request.get('origin_location_id')
    destination_location_id = request.get('destination_location_id')
    commodity = request.get('commodity')
    containers_count = request.get('containers_count')
    container_type = request.get('container_type')
    container_size = request.get('container_size')
    cargo_weight_per_container = request.get('cargo_weight_per_container')

    haulage_estimated_data = haulage_rate_calculator(
        origin_location_id,
        destination_location_id,
        commodity,
        containers_count,
        container_type,
        container_size,
        cargo_weight_per_container
    )

    if not haulage_estimated_data:
        return False
    haulage_estimated_data = [haulage_estimated_data]
    for data in haulage_estimated_data:
        list_items = data.get('list')
        line_items = list_items[0].get('line_items')
        detention_free_time = 1
        validity_start = datetime.now().date()
        validity_end = (datetime.now() + timedelta(days = 60)).date()
        cogo_envision_id = DEFAULT_USER_ID

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
            'transport_modes': HAULAGE_PREDICTION_TRANSPORT_MODES,
            'line_items': line_items,
            'transit_time': data.get('transit_time'),
            'detention_free_time': detention_free_time,
            'validity_start': validity_start,
            'validity_end': validity_end
        }

        create_haulage_freight_rate(params)

    return haulage_estimated_data
    
