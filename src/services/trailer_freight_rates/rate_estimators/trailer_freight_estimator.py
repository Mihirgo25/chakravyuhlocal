from database.db_session import db
from micro_services.client import maps
from configs.trailer_freight_rate_constants import *
from fastapi import HTTPException
from services.trailer_freight_rates.rate_estimators.IN_trailer_estimator import INTrailerRateEstimator
from services.trailer_freight_rates.rate_estimators.US_trailer_estimator import USTrailerRateEstimator


class TrailerFreightEstimator():
    def __init__(self, origin_location_id, destination_location_id, country_code):
        self.origin_location_id = origin_location_id
        self.destination_location_id = destination_location_id
        self.country_code = country_code

    def estimate(self, container_size, container_type, containers_count, cargo_weight_per_container):
        self.container_size = container_size
        self.container_type = container_type
        self.containers_count = containers_count
        self.cargo_weight_per_container = cargo_weight_per_container

        if self.country_code == "IN":
            estimator = INTrailerRateEstimator(self.origin_location_id, self.destination_location_id, self.country_code)
            return estimator.IN_estimate(container_size, container_type, containers_count, cargo_weight_per_container)
        
        if self.country_code == "US":
            estimator = USTrailerRateEstimator(self.origin_location_id, self.destination_location_id, self.country_code)
            return estimator.US_estimate(container_size, container_type, containers_count, cargo_weight_per_container)
        
        
        return {'list':[]}