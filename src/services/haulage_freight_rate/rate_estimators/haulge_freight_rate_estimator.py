from services.haulage_freight_rate.rate_estimators.india_haulage_freight_rate_estimator import (
    IndiaHaulageFreightRateEstimator,
)
from services.haulage_freight_rate.rate_estimators.china_haulage_freight_rate_estimation import (
    ChinaHaulageFreightRateEstimator,
)
from services.haulage_freight_rate.models.haulage_freight_rate_rule_sets import (
    HaulageFreightRateRuleSet,
)
import datetime
from micro_services.client import maps
import services.haulage_freight_rate.interactions.get_haulage_freight_rate_estimation as get_haulage_freight_rate_estimation
from configs.haulage_freight_rate_constants import (
    DESTINATION_TERMINAL_CHARGES_INDIA,
    CONTAINER_TYPE_CLASS_MAPPINGS,
    WAGON_COMMODITY_MAPPING,
    WAGON_MAPPINGS,
    SERVICE_PROVIDER_ID,
    DEFAULT_HAULAGE_TYPE,
    DEFAULT_TRIP_TYPE,
    CONTAINER_SIZE_FACTORS,
)
from configs.global_constants import COGO_ENVISION_ID



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
        location_category
    ):
        self.origin_location_id = origin_location_id
        self.destination_location_id = destination_location_id
        self.commodity = commodity
        self.containers_count = containers_count
        self.container_type = container_type
        self.cargo_weight_per_container = cargo_weight_per_container
        self.container_size = container_size
        self.location_category = location_category

    def estimate(self):
        if self.location_category == "India":
            estimator = IndiaHaulageFreightRateEstimator(
                origin_location_id=self.origin_location_id,
                destination_location_id=self.destination_location_id,
                commodity = self.commodity,
                containers_count = self.containers_count,
                cargo_weight_per_container = self.cargo_weight_per_container,
                container_size = self.container_size,
                location_category = self.location_category
            )
            price = estimator.estimate()
            print(price)
            return price

        if self.location_category == "China":
            estimator = ChinaHaulageFreightRateEstimator(
                origin_location_id=self.origin_location_id,
                destination_location_id=self.destination_location_id,
            )
            price = estimator.estimate()
            return {"is_price_estimated": True, "price": price}

        return {"is_price_estimated": False, "price": None}



    def get_container_and_commodity_type(
        self, commodity, container_type, location_category
    ):
        commodity = CONTAINER_TYPE_CLASS_MAPPINGS[container_type][0]
        permissable_carrying_capacity = WAGON_MAPPINGS[
            WAGON_COMMODITY_MAPPING[commodity]
        ][0]["permissable_carrying_capacity"]
        return commodity, permissable_carrying_capacity
