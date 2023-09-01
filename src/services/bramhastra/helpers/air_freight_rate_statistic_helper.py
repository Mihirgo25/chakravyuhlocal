from services.bramhastra.models.air_freight_rate_statistic import (
    AirFreightRateStatistic,
)
from services.bramhastra.enums import ValidityAction
from services.air_freight_rate.models.air_freight_location_cluster_mapping import (
    AirFreightLocationClusterMapping,
)
from services.air_freight_rate.models.air_freight_location_cluster import (
    AirFreightLocationCluster,
)
from micro_services.client import maps, common
from fastapi.encoders import jsonable_encoder
from services.bramhastra.helpers.common_statistic_helper import (
    get_air_freight_identifier,
)
from services.bramhastra.enums import Air

UPDATE_EXCLUDE_ITEMS = {
    "origin_airport_id",
    "origin_country_id",
    "origin_trade_id",
    "origin_continent_id",
    "destination_airport_id",
    "destination_country_id",
    "destination_trade_id",
    "destination_continent_id",
    "origin_region_id",
    "destination_region_id",
    "airline_id",
    "service_provider_id",
    "importer_exporter_id",
    "commodity",
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
        self.origin_region_id = None
        self.destination_region_id = None
        self.set_non_existing_location_details()

    def set_new_stats(self) -> int:
        return AirFreightRateStatistic.insert_many(self.params).execute()

    def create(self, row):
        return AirFreightRateStatistic.create(**row)

    def update(self, row):
        if (
            air_freight_rate_statistic := AirFreightRateStatistic.select()
            .where(
                AirFreightRateStatistic.identifier
                == get_air_freight_identifier(
                    row["rate_id"],
                    row["validity_id"],
                    row["lower_limit"],
                    row["upper_limit"],
                )
            )
            .first()
        ):
            for k, v in row.items():
                if k in UPDATE_EXCLUDE_ITEMS:
                    setattr(row, k, v)

            air_freight_rate_statistic.save()

    def set_existing_stats(self) -> None:
        for new_row in self.params:
            if new_row["last_action"] == ValidityAction.create.value:
                self.create(new_row)
            else:
                self.update(new_row)

    def set_non_existing_location_details(self) -> None:
        self.set_pricing_map_zone_ids(
            self.freight.origin_airport_id, self.freight.destination_airport_id
        )

        origin, destination = self.get_missing_location_ids(
            self.freight.origin_airport_id, self.freight.destination_airport_id
        )

        self.origin_region_id = origin.get("region_id")
        self.destination_region_id = destination.get("region_id")

    def set_formatted_data(self) -> None:
        freight = self.freight.dict(exclude={"validities", "weight_slabs"})

        for validity in self.freight.validities:
            for weight_slab in validity.weight_slabs:
                param = freight.copy()
                param.update(validity.dict(exclude={"weight_slabs"}))
                param["identifier"] = get_air_freight_identifier(
                    param["rate_id"],
                    param["validity_id"],
                    str(weight_slab.lower_limit),
                    str(weight_slab.upper_limit),
                )
                param["price"] = weight_slab.tariff_price
                param["lower_limit"] = weight_slab.lower_limit
                param["upper_limit"] = weight_slab.upper_limit
                param["origin_pricing_zone_map_id"] = self.origin_pricing_zone_map_id
                param[
                    "destination_pricing_zone_map_id"
                ] = self.destination_pricing_zone_map_id
                param["origin_region_id"] = self.origin_region_id
                param["destination_region_id"] = self.destination_region_id

                if param["currency"] == Air.default_currency.value:
                    param["standard_price"] = param["price"]
                else:
                    param["standard_price"] = common.get_money_exchange_for_fcl(
                        {
                            "from_currency": param["currency"],
                            "to_currency": Air.default_currency.value,
                            "price": param["price"],
                        }
                    ).get("price", param["price"])

                self.params.append(param)

    def set_pricing_map_zone_ids(
        self, origin_airport_id, destination_airport_id
    ) -> list:
        ids = [origin_airport_id, destination_airport_id]
        query = (
            AirFreightLocationCluster.select(
                AirFreightLocationClusterMapping.location_id,
                AirFreightLocationCluster.map_zone_id,
            )
            .join(AirFreightLocationClusterMapping)
            .where(AirFreightLocationClusterMapping.location_id.in_(ids))
        )
        map_zone_location_mapping = jsonable_encoder(
            {item["location_id"]: item["map_zone_id"] for item in query.dicts()}
        )

        if len(map_zone_location_mapping) < 2:
            query = AirFreightLocationCluster.select(
                AirFreightLocationCluster.base_airport_id.alias("location_id"),
                AirFreightLocationCluster.map_zone_id,
            ).where(AirFreightLocationCluster.base_airport_id.in_(ids))
            map_zone_location_mapping.update(
                jsonable_encoder(
                    {item["location_id"]: item["map_zone_id"] for item in query.dicts()}
                )
            )

        self.origin_pricing_zone_map_id = map_zone_location_mapping.get(
            origin_airport_id
        )
        self.destination_pricing_zone_map_id = map_zone_location_mapping.get(
            destination_airport_id
        )

    def get_missing_location_ids(self, origin_airport_id, destination_airport_id):
        response = maps.list_locations(
            data={
                "filters": {"id": [origin_airport_id, destination_airport_id]},
                "includes": {"region_id": True, "id": True},
            }
        )
        if "list" in response and len(response["list"]) == 2:
            region_id_mapping = {
                item["id"]: dict(region_id=item["region_id"])
                for item in response["list"]
            }
            return region_id_mapping.get(origin_airport_id), region_id_mapping.get(
                destination_airport_id
            )
        return None, None
