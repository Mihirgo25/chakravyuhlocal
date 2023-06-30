from services.trailer_freight_rate.rate_estimators.trailer_freight_estimator import TrailerFreightEstimator
from configs.trailer_freight_rate_constants import *
from micro_services.client import maps
from fastapi import HTTPException

def get_estimated_trailer_freight_rate(request):
    origin_location_id = request['origin_location_id']
    destination_location_id = request['destination_location_id']
    container_size = request['container_size']
    container_type = request['container_type'] if request['container_type'] else DEFAULT_CONTAINER_TYPE
    containers_count = request['containers_count']
    cargo_weight_per_container = request['cargo_weight_per_container'] if request.get('cargo_weight_per_container') is not None else DEFAULT_MAX_WEIGHT_LIMIT.get(container_size)
    trip_type = request['trip_type'] if request['trip_type'] is not None else DEFAULT_TRIP_TYPE
    if 'round' in trip_type:
        trip_type = 'round_trip'


    if origin_location_id == destination_location_id:
        raise HTTPException(status_code=400, detail="origin_location cannot be same as destination_location")

    input = {"filters":{"id":[origin_location_id, destination_location_id]}}
    data = maps.list_locations(input)
    if data and 'list' in data:
        data = data["list"]
    for d in data:
        if d["id"] == origin_location_id:
            country_code = d['country_code']

    country_code = country_code if country_code in CALCULATION_COUNTRY_CODES else DEFAULT_CALCULATION_COUNTRY_CODE
    
    estimator = TrailerFreightEstimator(origin_location_id, destination_location_id, country_code)
    return estimator.estimate(container_size, container_type, containers_count, cargo_weight_per_container, trip_type)