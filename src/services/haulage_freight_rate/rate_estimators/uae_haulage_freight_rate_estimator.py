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
    DEFAULT_MAX_WEIGHT_LIMIT,
    USD_TO_VND,
    CONTAINER_HANDLING_CHARGES
)
class UaeHaulageFreightRateEstimator:
    def __init__(self, query, commodity, load_type, containers_count, distance, container_type, cargo_weight_per_container, permissable_carrying_capacity, container_size, transit_time):
        self.query = query
        self.commodity = commodity
        self.load_type = load_type
        self.containers_count = containers_count
        self.distance = distance
        self.container_type = container_type
        self.cargo_weight_per_container = cargo_weight_per_container
        self.permissable_carrying_capacity = permissable_carrying_capacity
        self.container_size = container_size
        self.transit_time = transit_time

    def estimate(self):
        """
        Primary Function to estimate uae prices
        """
        final_price = self.get_uae_rates(
            query=self.query,
            commodity=self.commodity,
            load_type=self.load_type,
            containers_count=self.containers_count,
            location_pair_distance=self.distance,
            container_type=self.container_type,
            cargo_weight_per_container=self.cargo_weight_per_container,
            permissable_carrying_capacity=self.permissable_carrying_capacity,
            container_size=self.container_size,
            transit_time=self.transit_time
        )
        return final_price

    def get_uae_rates(
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
        transit_time
    ):
        final_data = {}
        final_data["distance"] = location_pair_distance
        location_pair_distance = float(location_pair_distance)
        query = query.where(
            HaulageFreightRateRuleSet.distance >= location_pair_distance,
            HaulageFreightRateRuleSet.commodity_class_type == commodity,
            HaulageFreightRateRuleSet.train_load_type == load_type,
        ).order_by(SQL("base_price ASC"))
        if query.count() == 0:
            raise HTTPException(status_code=400, detail="rates not present")
        price = model_to_dict(query.first())
        price_per_tonne_per_km = price["base_price"]
        currency = price["currency"]
        indicative_price = (float(price_per_tonne_per_km) * permissable_carrying_capacity) * CONTAINER_SIZE_FACTORS[container_size] * location_pair_distance
        final_data["base_price"] = self.apply_surcharges_for_uae(indicative_price, container_size)
        final_data["currency"] = currency
        final_data["transit_time"] = transit_time
        return final_data

    def apply_surcharges_for_uae(self, indicative_price, container_size):
        indicative_price = indicative_price
        surcharge = 0.15 * indicative_price
        development_charges = 0.05 * indicative_price
        tonnage_fees = 0.1*indicative_price 
        gst_charges = indicative_price * 0.05
        cargo_handling_charge = float(CONTAINER_HANDLING_CHARGES[container_size]['stuffed']['warehouse_to_automobile']) * float(USD_TO_VND)
        final_price =  indicative_price + surcharge + tonnage_fees + gst_charges + cargo_handling_charge
        return final_price