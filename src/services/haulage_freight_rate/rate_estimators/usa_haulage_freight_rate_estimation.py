from services.haulage_freight_rate.models.haulage_freight_rate_rule_sets import (
    HaulageFreightRateRuleSet,
)
class UsaHaulageFreightRateEstimator():
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



    def get_north_america_rates(commodity, load_type, container_count, ports_distance):
        final_data = {}
        final_data["distance"] = ports_distance
        final_data["currency"] = "USD"
        final_data["country_code"] = "US"

        wagon_upper_limit = (
            HaulageFreightRateRuleSet.select()
            .where(
                HaulageFreightRateRuleSet.commodity_class_type == commodity,
                HaulageFreightRateRuleSet.distance >= ports_distance,
                HaulageFreightRateRuleSet.train_load_type == load_type,
                HaulageFreightRateRuleSet.currency == "USD",
                HaulageFreightRateRuleSet.country_code == "US",
            )
            .order_by(HaulageFreightRateRuleSet.distance)
        )

        wagon_price_upper_limit = [model_to_dict(item) for item in wagon_upper_limit]

        if not wagon_price_upper_limit:
            raise HTTPException(status_code=400, detail="rates not present")


        price = wagon_price_upper_limit[0]["base_price"]
        price = price * container_count
        final_data["base_price"] = apply_surcharges_for_usa_europe(float(price))

        return final_data


    def get_europe_rates(commodity, load_type, container_count, ports_distance, wagon_type):
        final_data = {}
        final_data["distance"] = ports_distance
        final_data["currency"] = "EUR"
        final_data["country_code"] = "EU"

        wagon_upper_limit = (
            HaulageFreightRateRuleSet.select()
            .where(
                HaulageFreightRateRuleSet.commodity_class_type == commodity,
                HaulageFreightRateRuleSet.distance >= ports_distance,
                HaulageFreightRateRuleSet.train_load_type == load_type,
                HaulageFreightRateRuleSet.wagon_type == wagon_type,
                HaulageFreightRateRuleSet.currency == "EUR",
                HaulageFreightRateRuleSet.country_code == "EU",
            )
            .order_by(HaulageFreightRateRuleSet.distance)
        )
        wagon_price_upper_limit = [model_to_dict(item) for item in wagon_upper_limit]

        if not wagon_price_upper_limit:
            raise HTTPException(status_code=400, detail="rates not present")

        price = wagon_price_upper_limit[0]["base_price"]
        price = price * container_count
        final_data["base_price"] = apply_surcharges_for_usa_europe(float(price))

        return final_data
