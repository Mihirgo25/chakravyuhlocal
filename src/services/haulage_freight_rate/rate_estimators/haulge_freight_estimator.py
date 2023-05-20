from services.haulage_freight_rate.rate_estimators.IN_haulage_estimator import INHaulageRateEstimator

class HaulageFreightEstimator():
    def __init__(self, origin_location_id, destination_location_id, country_code):
        self.origin_location_id = origin_location_id,
        self.destination_location_id = destination_location_id,
        self.country_code = country_code

    def estimate(self):
        if self.country_code == 'IN':
            estimator = INHaulageRateEstimator(origin_location_id= self.origin_location_id, destination_location_id= self.destination_location_id)
            price = estimator.estimate()
            return { 'is_price_estimated': True, 'price': price }

        return { 'is_price_estimated': False, 'price': None }

