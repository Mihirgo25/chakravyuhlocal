from services.haulage_freight_rate.models.haulage_freight_rate_rule_sets import (
    HaulageFreightRateRuleSet,
)
from fastapi import HTTPException

class GeneralizedHaulageFreightRateEstimator():
    def __init__(self, origin_location_id, destination_location_id):
        self.origin_location_id = origin_location_id,
        self.destination_location_id = destination_location_id

    def convert_general_params_to_estimation_params(self):
        return True

    def get_final_estimated_price(self, estimator_params):
        return 10


    def apply_surcharges_for_usa_europe(self, price):
        surcharge = 0.15 * price
        development_charges = 0.05 * price
        final_price = price + surcharge + development_charges

        return final_price


    def estimate(self):
        '''
        Primary Function to estimate india prices
        '''
        print('Estimating India rates')
        estimator_params = self.convert_general_params_to_estimation_params()
        final_price = self.get_final_estimated_price(estimator_params=estimator_params)
        return final_price



    def get_generalized_rates(
        self,
        query,
        commodity,
        load_type,
        containers_count,
        location_pair_distance,
        container_type,
        cargo_weight_per_container,
        permissable_carrying_capacity,
        container_size,
    ):
        final_data = {}
        final_data["distance"] = location_pair_distance
        raise HTTPException(status_code=400, detail="rates not present")


