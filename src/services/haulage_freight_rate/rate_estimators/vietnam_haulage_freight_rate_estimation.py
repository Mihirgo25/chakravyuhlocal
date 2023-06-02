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
    DEFAULT_MAX_WEIGHT_LIMIT
)

class VietnamHaulageFreightRateEstimator:
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
        Primary Function to estimate vietnam prices
        """
        final_price = self.get_vietnam_rates(
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

    def get_vietnam_rates(
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

            HaulageFreightRateRuleSet.container_type == container_size,
            HaulageFreightRateRuleSet.train_load_type == load_type,
        ).order_by(SQL("base_price ASC"))