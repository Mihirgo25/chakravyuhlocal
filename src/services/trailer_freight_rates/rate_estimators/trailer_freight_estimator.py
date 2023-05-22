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

        input = {"filters":{"id":[self.origin_location_id, self.destination_location_id]}}
        data = maps.list_locations(input)
        if data:
            data = data["list"]
        for d in data:
            if d["id"] == self.origin_location_id:
                origin_country_code = d['country_code']
            if d["id"] == self.destination_location_id:
                destination_country_code = d['country_code']
        
        if origin_country_code!=destination_country_code:
            raise HTTPException(status_code=404, detail="Origin and destination country should be same")

        self.country_code = origin_country_code

        if self.country_code == "IN":
            estimator = INTrailerRateEstimator
            return estimator.estimate(self)
        
        if self.country_code == "US":
            estimator = USTrailerRateEstimator
            return estimator.estimate(self)
        
        return {'list':[]}