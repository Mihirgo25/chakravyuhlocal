from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from services.bramhastra.enums import ValidityAction
from services.fcl_freight_rate.models.fcl_freight_location_cluster_mapping import (
    FclFreightLocationClusterMapping,
    FclFreightLocationCluster,
)
from micro_services.client import common
from fastapi.encoders import jsonable_encoder
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from services.fcl_freight_rate.models.fcl_freight_rate_feedback import (
    FclFreightRateFeedback,
)
from services.bramhastra.constants import FCL_MODE_MAPPINGS
from services.bramhastra.enums import FclModes, Fcl
from services.bramhastra.helpers.common_statistic_helper import get_identifier

UPDATE_EXCLUDE_ITEMS = {
    "origin_port_id",
    "origin_country_id",
    "origin_trade_id",
    "origin_continent_id",
    "destination_port_id",
    "destination_country_id",
    "destination_trade_id",
    "destination_continent_id",
    "origin_region_id",
    "destination_region_id",
    "shipping_line_id",
    "service_provider_id",
    "importer_exporter_id",
    "container_size",
    "container_type",
    "commodity",
    "origin_main_port_id",
    "destination_main_port_id",
    "procured_by_id",
    "rate_id",
    "validity_id",
    "identifier",
}


class Rate:
    def __init__(self, freight) -> None:
        self.freight = freight
        self.params = []
        self.origin_pricing_zone_map_id = None
        self.destination_pricing_zone_map_id = None
        self.increment_keys = {}

    def create(self, row) -> None:
        FclFreightRateStatistic.create(**row)

    def update(self, row) -> None:
        fcl_freight_rate_statistic = (
            FclFreightRateStatistic.select()
            .where(
                FclFreightRateStatistic.identifier
                == get_identifier(row.get("rate_id", "validity_id"))
            )
            .first()
        )

        for k, v in row.items():
            if k not in UPDATE_EXCLUDE_ITEMS and v:
                setattr(fcl_freight_rate_statistic, k, v)

        fcl_freight_rate_statistic.save()

    def set_new_stats(self) -> int:
        return FclFreightRateStatistic.insert_many(self.params).execute()

    def set_existing_stats(self) -> None:
        for row in self.params:
            if row["last_action"] == ValidityAction.create.value:
                self.create(row)
            elif row["last_action"] == ValidityAction.update.value:
                self.update(row)
            elif row["last_action"] == ValidityAction.unchanged.value:
                self.update(row)

    def get_feedback_details(self):
        if row := (
            FclFreightRateFeedback.select(
                FclFreightRateFeedback.fcl_freight_rate_id.alias("parent_rate_id"),
                FclFreightRateFeedback.validity_id.alias("parent_validity_id"),
            )
            .where(FclFreightRateFeedback.id == self.freight.source_id)
            .dicts()
        ):
            return jsonable_encoder(row.get())

    def set_formatted_data(self) -> None:
        freight = self.freight.dict(exclude={"validities", "accuracy"})

        freight["parent_mode"] = FCL_MODE_MAPPINGS.get(
            freight.get("mode") or FclModes.rms_upload.value
        )

        if (
            freight["source"] == FclModes.disliked_rate.value
            or freight.get("mode") == FclModes.disliked_rate.value
        ):
            if parent := self.get_feedback_details():
                freight.update(parent)
                self.increment_keys.add("dislikes_rate_reverted_count")
                
        if freight["source"] == FclModes.missing_rate.value:
            self.increment_keys.add("reverted_rates_count")

        for validity in self.freight.validities:
            param = freight.copy()
            param.update(validity.dict(exclude={"line_items"}))
            param["identifier"] = get_identifier(
                param["rate_id"], param["validity_id"]
            )
            param["origin_pricing_zone_map_id"] = self.origin_pricing_zone_map_id
            param[
                "destination_pricing_zone_map_id"
            ] = self.destination_pricing_zone_map_id

            if param["currency"] == Fcl.default_currency.value:
                param["standard_price"] = param["price"]
            else:
                param["standard_price"] = common.get_money_exchange_for_fcl(
                    {
                        "from_currency": param["currency"],
                        "to_currency": Fcl.default_currency.value,
                        "price": param["price"],
                    }
                ).get("price", param["price"])

            self.params.append(param)

    def set_pricing_map_zone_ids(self) -> list:
        ids = [self.freight.origin_port_id, self.freight.destination_port_id]
        query = (
            FclFreightLocationCluster.select(
                FclFreightLocationClusterMapping.location_id,
                FclFreightLocationCluster.map_zone_id,
            )
            .join(FclFreightLocationClusterMapping)
            .where(FclFreightLocationClusterMapping.location_id.in_(ids))
        )
        map_zone_location_mapping = jsonable_encoder(
            {item["location_id"]: item["map_zone_id"] for item in query.dicts()}
        )

        if len(map_zone_location_mapping) < 2:
            query = FclFreightLocationCluster.select(
                FclFreightLocationCluster.base_port_id.alias("location_id"),
                FclFreightLocationCluster.map_zone_id,
            ).where(FclFreightLocationCluster.base_port_id.in_(ids))
            map_zone_location_mapping.update(
                jsonable_encoder(
                    {item["location_id"]: item["map_zone_id"] for item in query.dicts()}
                )
            )

        self.origin_pricing_zone_map_id = map_zone_location_mapping.get(
            self.freight.origin_port_id
        )

        self.destination_pricing_zone_map_id = map_zone_location_mapping.get(
            self.freight.destination_port_id
        )
