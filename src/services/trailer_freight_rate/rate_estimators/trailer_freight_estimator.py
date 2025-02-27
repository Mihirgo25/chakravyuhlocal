from database.db_session import db
from micro_services.client import maps
from configs.trailer_freight_rate_constants import *
from fastapi import HTTPException
from services.trailer_freight_rate.rate_estimators.IN_trailer_estimator import INTrailerRateEstimator
from services.trailer_freight_rate.rate_estimators.US_trailer_estimator import USTrailerRateEstimator
from services.trailer_freight_rate.rate_estimators.CN_trailer_estimator import CNTrailerRateEstimator
from services.trailer_freight_rate.rate_estimators.VN_trailer_estimator import VNTrailerRateEstimator
from services.trailer_freight_rate.rate_estimators.SouthAmerica_trailer_estimator import SouthAmericaTrailerRateEstimator
from services.trailer_freight_rate.rate_estimators.ID_trailer_estimator import IDTrailerRateEstimator
from services.trailer_freight_rate.rate_estimators.SG_trailer_estimator import SGTrailerRateEstimator
from services.trailer_freight_rate.rate_estimators.AE_trailer_estimator import AETrailerRateEstimator
from services.trailer_freight_rate.rate_estimators.RU_trailer_estimator import RUTrailerRateEstimator

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
        
        '''For South America'''
        if self.country_code == "BR" or self.country_code == "AQ" or self.country_code == "CO":
            estimator = SouthAmericaTrailerRateEstimator(self.origin_location_id, self.destination_location_id, self.country_code)
            return estimator.SouthAmerica_estimate(container_size, container_type, containers_count, cargo_weight_per_container, trip_type)
        
        if self.country_code == "ID":
            estimator  = IDTrailerRateEstimator(self.origin_location_id, self.destination_location_id, self.country_code)
            return estimator.ID_estimate(container_size, container_type, containers_count, cargo_weight_per_container, trip_type)
        
        if self.country_code == "SG":
            estimator  = SGTrailerRateEstimator(self.origin_location_id, self.destination_location_id, self.country_code)
            return estimator.SG_estimate(container_size, container_type, containers_count, cargo_weight_per_container, trip_type)
        
        if self.country_code == "AE":
            estimator  = AETrailerRateEstimator(self.origin_location_id, self.destination_location_id, self.country_code)
            return estimator.AE_estimate(container_size, container_type, containers_count, cargo_weight_per_container, trip_type)
        
        if self.country_code == "RU":
            estimator  = RUTrailerRateEstimator(self.origin_location_id, self.destination_location_id, self.country_code)
            return estimator.RU_estimate(container_size, container_type, containers_count, cargo_weight_per_container, trip_type)
        
        return {'list':[]}