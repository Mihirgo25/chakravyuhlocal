from services.trailer_freight_rates.rate_estimators.trailer_freight_estimator import TrailerFreightEstimator
from configs.trailer_freight_rate_constants import *
from micro_services.client import maps
from fastapi import HTTPException

def get_estimated_rate(request):
    origin_location_id = request['origin_location_id']
    destination_location_id = request['destination_location_id']
    container_size = request['container_size']
    container_type = request['container_type']
    containers_count = request['containers_count']
    cargo_weight_per_container = request['cargo_weight_per_container'] if request.get('cargo_weight_per_container') is not None else DEFAULT_MAX_WEIGHT_LIMIT.get(container_size)

    input = {"filters":{"id":[origin_location_id, destination_location_id]}}
    data = maps.list_locations(input)
    if data:
        data = data["list"]
    for d in data:
        if d["id"] == origin_location_id:
            country_code = d['country_code']

    country_code = country_code if country_code in CALCULATION_COUNTRY_CODES else DEFAULT_CALCULATION_COUNTRY_CODE
    
    estimator = TrailerFreightEstimator(origin_location_id, destination_location_id, country_code)
    return estimator.estimate(container_size, container_type, containers_count, cargo_weight_per_container)