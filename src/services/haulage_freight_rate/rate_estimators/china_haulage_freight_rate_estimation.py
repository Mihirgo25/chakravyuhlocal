class ChinaHaulageFreightRateEstimator():
    def __init__(self, origin_location_id, destination_location_id):
        self.origin_location_id = origin_location_id,
        self.destination_location_id = destination_location_id

    def convert_general_params_to_estimation_params(self):
        return True

    def get_final_estimated_price(self, estimator_params):
        return 10


    def estimate(self):
        '''
        Primary Function to estimate india prices
        '''
        print('Estimating India rates')
        estimator_params = self.convert_general_params_to_estimation_params()
        final_price = self.get_final_estimated_price(estimator_params=estimator_params)
        return final_price



    def get_china_rates(
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
        query = (
            query.where(
                HaulageFreightRateRuleSet.container_type == container_size,
                HaulageFreightRateRuleSet.train_load_type == load_type,
            )
            .order_by(SQL("base_price ASC"))
        )

        if query.count()==0:
            raise HTTPException(status_code=400, detail="rates not present")
        price = model_to_dict(query.first())
        currency = price["currency"]
        price_per_container = float(price["base_price"])
        running_base_price_per_carton_km = float(price["running_base_price"])
        base_price = price_per_container * containers_count
        running_base_price = (
            running_base_price_per_carton_km
            * cargo_weight_per_container
            * float(location_pair_distance)
        )
        indicative_price = base_price + running_base_price

        final_data["base_price"] = apply_surcharges(indicative_price)
        final_data["currency"] = currency
        final_data["transit_time"] = get_transit_time(location_pair_distance)
        return final_data
