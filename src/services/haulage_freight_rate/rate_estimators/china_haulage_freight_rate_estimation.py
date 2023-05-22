from services.haulage_freight_rate.models.haulage_freight_rate_rule_sets import (
    HaulageFreightRateRuleSet,
)
from fastapi import HTTPException
from playhouse.shortcuts import model_to_dict
from playhouse.postgres_ext import SQL
from services.haulage_freight_rate.helpers.haulage_freight_rate_helpers import (
    get_transit_time,
)
from configs.haulage_freight_rate_constants import (
    CONTAINER_SIZE_FACTORS,
    DESTINATION_TERMINAL_CHARGES_INDIA,
)
class ChinaHaulageFreightRateEstimator():
    def __init__(self, *_, **__): pass

    def estimate(self):
        '''
        Primary Function to estimate china prices
        '''
        instance = ChinaHaulageFreightRateEstimator()
        final_price = instance.get_china_rates(query=self.query,
            commodity=self.commodity,
            load_type=self.load_type,
            containers_count=self.containers_count,
            location_pair_distance=self.distance,
            container_type=self.container_type,
            cargo_weight_per_container=self.cargo_weight_per_container,
            permissable_carrying_capacity=self.permissable_carrying_capacity,
            container_size=self.container_size,)
        return final_price



    def get_china_rates(
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

        final_data["base_price"] = self.apply_surcharges_for_china(indicative_price)
        final_data["currency"] = currency
        final_data["transit_time"] = get_transit_time(location_pair_distance)
        return final_data

    def apply_surcharges_for_china(self, indicative_price):
        surcharge = 0.15 * indicative_price
        development_charges = 0.05 * indicative_price
        other_charges = development_charges
        taxes = indicative_price * 0.05
        final_price = indicative_price + surcharge + other_charges + taxes
        return final_price
