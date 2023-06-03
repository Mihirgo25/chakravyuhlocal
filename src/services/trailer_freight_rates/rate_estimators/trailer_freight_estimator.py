from database.db_session import db
from micro_services.client import maps
from configs.trailer_freight_rate_constants import *
from fastapi import HTTPException
from services.trailer_freight_rates.rate_estimators.IN_trailer_estimator import INTrailerRateEstimator
from services.trailer_freight_rates.rate_estimators.US_trailer_estimator import USTrailerRateEstimator
from services.trailer_freight_rates.rate_estimators.CN_trailer_estimator import CNTrailerRateEstimator
from services.trailer_freight_rates.rate_estimators.VN_trailer_estimator import VNTrailerRateEstimator


class TrailerFreightEstimator():
    def __init__(self, origin_location_id, destination_location_id, country_code):
        self.origin_location_id = origin_location_id
        self.destination_location_id = destination_location_id
        self.country_code = country_code

    def estimate(self, container_size, container_type, containers_count, cargo_weight_per_container, trip_type):
        self.container_size = container_size
        self.container_type = container_type
        self.containers_count = containers_count
        self.cargo_weight_per_container = cargo_weight_per_container
        self.trip_type = trip_type

        if self.country_code == "IN":
            estimator = INTrailerRateEstimator(self.origin_location_id, self.destination_location_id, self.country_code)
            return estimator.IN_estimate(container_size, container_type, containers_count, cargo_weight_per_container, trip_type)
        
        '''For North America'''
        if self.country_code == "US" or self.country_code == "CA" or self.country_code == "MX":
            estimator = USTrailerRateEstimator(self.origin_location_id, self.destination_location_id, self.country_code)
            return estimator.US_estimate(container_size, container_type, containers_count, cargo_weight_per_container, trip_type)
        
        if self.country_code == "CN":
            estimator = CNTrailerRateEstimator(self.origin_location_id, self.destination_location_id, self.country_code)
            return estimator.CN_estimate(container_size, container_type, containers_count, cargo_weight_per_container, trip_type)
        
        if self.country_code == "VN":
            estimator = VNTrailerRateEstimator(self.origin_location_id, self.destination_location_id, self.country_code)
            return estimator.VN_estimate(container_size, container_type, containers_count, cargo_weight_per_container, trip_type)
        
        
        return {'list':[]}