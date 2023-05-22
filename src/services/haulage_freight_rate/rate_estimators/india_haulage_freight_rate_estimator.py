from services.haulage_freight_rate.models.haulage_freight_rate_rule_sets import (
    HaulageFreightRateRuleSet,
)
from fastapi import HTTPException
from playhouse.shortcuts import model_to_dict
from configs.haulage_freight_rate_constants import (
    CONTAINER_SIZE_FACTORS,
    DESTINATION_TERMINAL_CHARGES_INDIA,
)
from playhouse.postgres_ext import SQL
from services.haulage_freight_rate.helpers.haulage_freight_rate_helpers import (
    get_transit_time,
)


class IndiaHaulageFreightRateEstimator:
    def __init__(
        self,
        query,
        load_type,
        distance,
        commodity,
        containers_count,
        container_type,
        cargo_weight_per_container,
        container_size,
        permissable_carrying_capacity,
    ):
        self.query = query
        self.load_type = load_type
        self.distance = distance
        self.commodity = commodity
        self.container_type = container_type
        self.containers_count = containers_count
        self.cargo_weight_per_container = cargo_weight_per_container
        self.container_size = container_size
        self.permissable_carrying_capacity = permissable_carrying_capacity

    def estimate(self):
        """
        Primary Function to estimate india prices
        """
        final_price = self.get_india_rates(
            query=self.query,
            commodity=self.commodity,
            load_type=self.load_type,
            containers_count=self.containers_count,
            location_pair_distance=self.distance,
            container_type=self.container_type,
            cargo_weight_per_container=self.cargo_weight_per_container,
            permissable_carrying_capacity=self.permissable_carrying_capacity,
            container_size=self.container_size,
        )
        return final_price

    def apply_surcharges_for_india(self, indicative_price):
        surcharge = 0.15 * indicative_price
        development_charges = 0.05 * indicative_price
        other_charges = development_charges + DESTINATION_TERMINAL_CHARGES_INDIA
        gst_charges = indicative_price * 0.05
        final_price = indicative_price + surcharge + other_charges + gst_charges
        return final_price

    def get_india_rates(
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
        if containers_count > 50:
            full_rake_count = containers_count / 50
            remaining_wagons_count = containers_count % 50
            rake_price = query.where(
                HaulageFreightRateRuleSet.distance >= location_pair_distance,
                HaulageFreightRateRuleSet.commodity_class_type == commodity,
                HaulageFreightRateRuleSet.train_load_type == "Train Load",
            ).order_by(SQL("base_price ASC"))
            wagon_price = query.where(
                HaulageFreightRateRuleSet.distance >= location_pair_distance,
                HaulageFreightRateRuleSet.commodity_class_type == commodity,
                HaulageFreightRateRuleSet.train_load_type == "Wagon Load",
            ).order_by(SQL("base_price ASC"))
            if rake_price.count() == 0 or wagon_price.count() == 0:
                raise HTTPException(status_code=400, detail="rates not present")
            rake_price_per_tonne = model_to_dict(rake_price.first())["base_price"]
            wagon_price_per_tonne = model_to_dict(wagon_price.first())["base_price"]

            if not rake_price_per_tonne or not wagon_price_per_tonne:
                raise HTTPException(status_code=400, detail="rates not present")

            currency = model_to_dict(wagon_price)["currency"]
            final_rake_price = (
                float(rake_price_per_tonne)
                * full_rake_count
                * 50
                * permissable_carrying_capacity
            )
            final_wagon_price = (
                float(wagon_price_per_tonne)
                * remaining_wagons_count
                * permissable_carrying_capacity
            )
            indicative_price = final_rake_price + final_wagon_price
        else:
            if location_pair_distance < 125:
                location_pair_distance = 125
            query = query.where(
                HaulageFreightRateRuleSet.distance >= location_pair_distance,
                HaulageFreightRateRuleSet.commodity_class_type == commodity,
                HaulageFreightRateRuleSet.train_load_type == load_type,
            ).order_by(SQL("base_price ASC"))
            if query.count() == 0:
                raise HTTPException(status_code=400, detail="rates not present")

            price = model_to_dict(query.first())
            price_per_tonne = price["base_price"]
            currency = price["currency"]

            indicative_price = (
                float(price_per_tonne)
                * containers_count
                * permissable_carrying_capacity
            ) * CONTAINER_SIZE_FACTORS[container_size]
        final_data["base_price"] = self.apply_surcharges_for_india(indicative_price)

        final_data["currency"] = currency
        final_data["transit_time"] = get_transit_time(location_pair_distance)

        return final_data
