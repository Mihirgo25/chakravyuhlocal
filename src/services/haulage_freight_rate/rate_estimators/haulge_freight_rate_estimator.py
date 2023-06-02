from services.haulage_freight_rate.rate_estimators.india_haulage_freight_rate_estimator import (
    IndiaHaulageFreightRateEstimator,
)
from services.haulage_freight_rate.rate_estimators.china_haulage_freight_rate_estimation import (
    ChinaHaulageFreightRateEstimator,
)
from services.haulage_freight_rate.rate_estimators.europe_haulage_freight_rate_estimation import (
    EuropeHaulageFreightRateEstimator,
)
from services.haulage_freight_rate.rate_estimators.vietnam_haulage_freight_rate_estimation import (
    VietnamHaulageFreightRateEstimator,
)
from services.haulage_freight_rate.rate_estimators.north_america_haulage_freight_rate_estimation import (
    NorthAmericaHaulageFreightRateEstimator,
)
from services.haulage_freight_rate.rate_estimators.generalized_haulage_freight_rate_estimator import (
    GeneralizedHaulageFreightRateEstimator,
)
from services.haulage_freight_rate.models.haulage_freight_rate_rule_sets import (
    HaulageFreightRateRuleSet,
)
import services.haulage_freight_rate.interactions.get_estimated_haulage_freight_rate as get_estimated_haulage_freight_rate
from configs.haulage_freight_rate_constants import (
    CONTAINER_TYPE_CLASS_MAPPINGS,
    WAGON_COMMODITY_MAPPING,
)
from services.haulage_freight_rate.models.wagon_types import WagonTypes

POSSIBLE_LOCATION_CATEGORY = [
    "india",
    "china",
    "europe",
    "north_america",
    "generalized",
]
from services.haulage_freight_rate.helpers.haulage_freight_rate_helpers import *


class HaulageFreightRateEstimator:
    def __init__(
        self,
        origin_location_id,
        destination_location_id,
        commodity,
        containers_count,
        container_type,
        cargo_weight_per_container,
        container_size,
    ):
        self.origin_location_id = origin_location_id
        self.destination_location_id = destination_location_id
        self.commodity = commodity
        self.containers_count = containers_count
        self.container_type = container_type
        self.cargo_weight_per_container = cargo_weight_per_container
        self.container_size = container_size

    def estimate(self):
        locations_data, location_category = self.get_location_data_and_category()
        self.convert_general_params_to_estimation_params(location_category)
        if location_category == "india":
            estimator = IndiaHaulageFreightRateEstimator(
                self.query,
                self.commodity,
                self.load_type,
                self.containers_count,
                self.distance,
                self.container_type,
                self.cargo_weight_per_container,
                self.permissable_carrying_capacity,
                self.container_size,
                self.transit_time,
            )

        elif location_category == "china":
            estimator = ChinaHaulageFreightRateEstimator(
                self.query,
                self.commodity,
                self.load_type,
                self.containers_count,
                self.distance,
                self.container_type,
                self.cargo_weight_per_container,
                self.permissable_carrying_capacity,
                self.container_size,
                self.transit_time,
            )

        elif location_category == "vietnam":
            """
            Estimation of haulage rate for vietnam
            """
            estimator = VietnamHaulageFreightRateEstimator(
                self.query,
                self.commodity,
                self.load_type,
                self.containers_count,
                self.distance,
                self.container_type,
                self.cargo_weight_per_container,
                self.permissable_carrying_capacity,
                self.container_size,
                self.transit_time,
            )
        elif location_category == "europe":
            """
            Estimation of haulage rate for european countries (Majorly for France, Norway, Netherlands, Germany, Switzerland)
            """
            estimator = EuropeHaulageFreightRateEstimator(
                self.commodity, self.load_type, self.containers_count, self.distance
            )

        elif location_category == "north_america":
            estimator = NorthAmericaHaulageFreightRateEstimator(
                self.commodity, self.load_type, self.containers_count, self.distance
            )

        else:
            estimator = GeneralizedHaulageFreightRateEstimator(self)

        price = estimator.estimate()
        line_items_data = build_line_item(
            self.origin_location_id,
            self.destination_location_id,
            price["base_price"],
            price["currency"],
            locations_data,
        )
        price["line_items"] = line_items_data
        return price

    def get_location_data_and_category(self):
        locations_data, location_category = get_country_filter(
            self.origin_location_id, self.destination_location_id
        )
        if location_category not in POSSIBLE_LOCATION_CATEGORY:
            return {"is_price_estimated": False, "price": None}

        location_pair_distance, transit_time = get_distances(
            self.origin_location_id, self.destination_location_id, locations_data
        )
        self.distance = location_pair_distance
        self.transit_time = transit_time
        return locations_data, location_category

    def convert_general_params_to_estimation_params(self, location_category):
        query = HaulageFreightRateRuleSet.select(
            HaulageFreightRateRuleSet.base_price,
            HaulageFreightRateRuleSet.running_base_price,
            HaulageFreightRateRuleSet.currency,
        )
        self.query = query
        if not self.containers_count:
            self.containers_count = 1
            self.load_type = "Wagon Load"
        else:
            self.load_type = "Wagon Load"
        (
            self.commodity,
            self.permissable_carrying_capacity,
        ) = self.get_container_and_commodity_type(self.commodity, self.container_type, location_category)

    def get_container_and_commodity_type(self, commodity, container_type, location_category):
        commodity = CONTAINER_TYPE_CLASS_MAPPINGS[container_type][location_category]
        permissable_carrying_capacity = list(
            WagonTypes.select(WagonTypes.permissible_carrying_capacity)
            .where(WagonTypes.wagon_type == WAGON_COMMODITY_MAPPING[commodity])
            .dicts()
        )[0]["permissible_carrying_capacity"]
        return commodity, permissable_carrying_capacity
