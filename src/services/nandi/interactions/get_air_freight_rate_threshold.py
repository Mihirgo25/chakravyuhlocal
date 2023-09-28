from services.nandi.models.air_freight_rate_threshold_limit import AirFreightRateThresholdLimit
from micro_services.client import common
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
from services.bramhastra.interactions.list_air_freight_rate_statistics import list_air_freight_rate_statistics
import asyncio

DEFAULT_MIN_THRESHOLD = 100
DEFAULT_MAX_THRESHOLD = 100

def air_freight_error_detection(data):
    print(data)
    origin_airport_id = data.get('origin_airport_id')
    destination_airport_id = data.get('destination_airport_id')
    airline_id = data.get('airline_id')
    rate_type = data.get("rate_type")

    filters = {
        "group_by":[
            "origin_airport_id",
            "destination_airport_id",
            "airline_id",
            "lower_limit",
            "upper_limit"
        ],
        "select":[
            "origin_airport_id",
            "destination_airport_id",
            "airline_id",
            "lower_limit",
            "upper_limit"
        ],
        "origin_airport_id": origin_airport_id,
        "destination_airport_id": destination_airport_id,
        "airline_id": airline_id,
        "rate_type": rate_type,
        "commodity": data.get('commodity'),
        'commodity_type': data.get('commodity_type'),
        "query_type": "aggregate",
        "validity_end_less_than": str(datetime.now().date()),
        "validity_end_greater_than": str(datetime.now().date() - relativedelta(months=1))
    }

    air_freight_rates = asyncio.run(list_air_freight_rate_statistics(filters = filters, page_limit = 10, page = 1, is_service_object_required = False,pagination_data_required=False))

    avg_prices = {}
    print(air_freight_rates)
    if len(air_freight_rates.get('list') or []):
        for weight_slab in air_freight_rates['list']:
            key = "{}_{}".format(weight_slab['lower_limit'],weight_slab['upper_limit'])
            avg_prices[key] = {'standard_price':0,'min_threshold':0,'max_threshold':0}
            avg_prices[key]['standard_price'] = weight_slab['standard_price']
    else:
        return True,{}

    threshold = AirFreightRateThresholdLimit.select(
        AirFreightRateThresholdLimit.min_threshold,
        AirFreightRateThresholdLimit.max_threshold,
        AirFreightRateThresholdLimit.min_threshold_type,
        AirFreightRateThresholdLimit.max_threshold_type).where(
        AirFreightRateThresholdLimit.airline_id == airline_id,
        AirFreightRateThresholdLimit.origin_airport_id == origin_airport_id,
        AirFreightRateThresholdLimit.destination_airport_id == destination_airport_id
    ).first()

    if not threshold:
        params = {
            'min_threshold': DEFAULT_MIN_THRESHOLD,
            'max_threshold': DEFAULT_MAX_THRESHOLD,
            'min_threshold_type': 'percent',
            'max_threshold_type': 'percent'
        }
        threshold = AirFreightRateThresholdLimit(**params)

    for weight_slab in avg_prices:
        avg_prices[weight_slab]['min_threshold'] = avg_prices[key]['standard_price'] * (100 - threshold.min_threshold) / 100 if threshold.min_threshold_type.lower() == 'percent' else (avg_prices[key]['standard_price'] - threshold.min_threshold)
        avg_prices[weight_slab]['max_threshold'] = avg_prices[key]['standard_price'] * (100 + threshold.max_threshold) / 100 if threshold.max_threshold_type.lower() == 'percent' else (avg_prices[key]['standard_price'] + threshold.max_threshold)
            
    for weight_slab in data.get('weight_slabs'):
        key = "{}_{}".format(weight_slab['lower_limit'],weight_slab['upper_limit'])
        if key in avg_prices:
            if weight_slab['tariff_price'] < avg_prices[key]['min_threshold'] or weight_slab['tariff_price'] > avg_prices[key]['max_threshold']:
                return False,avg_prices

    return True,{}