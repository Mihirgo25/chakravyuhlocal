from services.haulage_freight_rate.rate_estimators.india_haulage_freight_rate_estimator import (
    IndiaHaulageFreightRateEstimator,
)
from services.haulage_freight_rate.rate_estimators.china_haulage_freight_rate_estimation import (
    ChinaHaulageFreightRateEstimator,
)
from services.haulage_freight_rate.models.haulage_freight_rate_rule_sets import (
    HaulageFreightRateRuleSet,
)
import services.haulage_freight_rate.interactions.get_haulage_freight_rate_estimation as get_haulage_freight_rate_estimation
from configs.haulage_freight_rate_constants import (
    CONTAINER_TYPE_CLASS_MAPPINGS,
    WAGON_COMMODITY_MAPPING,
    WAGON_MAPPINGS,
)


class HaulageFreightRateEstimator:
    def __init__(
        self,
        distance,
        commodity,
        containers_count,
        container_type,
        cargo_weight_per_container,
        container_size,
        location_category,
    ):
        self.distance = distance
        self.commodity = commodity
        self.containers_count = containers_count
        self.container_type = container_type
        self.cargo_weight_per_container = cargo_weight_per_container
        self.container_size = container_size
        self.location_category = location_category

    def estimate(self):
        query = HaulageFreightRateRuleSet.select(
            HaulageFreightRateRuleSet.base_price,
            HaulageFreightRateRuleSet.running_base_price,
            HaulageFreightRateRuleSet.currency,
        )
        if not self.containers_count:
            self.containers_count = 1
            load_type = "Wagon Load"
        else:
            load_type = "Wagon Load"
        (
            commodity,
            permissable_carrying_capacity,
        ) = self.get_container_and_commodity_type(
            self.commodity, self.container_type, self.location_category
        )

        if self.location_category == "india":
            estimator = IndiaHaulageFreightRateEstimator
            price = estimator.estimate(self)
            return price

        if self.location_category == "china":
            estimator = ChinaHaulageFreightRateEstimator
            price = estimator.estimate(self)
            return price

        return {"is_price_estimated": False, "price": None}

    def get_container_and_commodity_type(
        self, commodity, container_type, location_category
    ):
        commodity = CONTAINER_TYPE_CLASS_MAPPINGS[container_type][0]
        permissable_carrying_capacity = WAGON_MAPPINGS[
            WAGON_COMMODITY_MAPPING[commodity]
        ][0]["permissable_carrying_capacity"]
        return commodity, permissable_carrying_capacity
