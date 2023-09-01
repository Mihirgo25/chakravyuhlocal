from services.fcl_freight_rate.models.fcl_freight_location_cluster_mapping import (
    FclFreightLocationClusterMapping,
    FclFreightLocationCluster,
)
from micro_services.client import maps
from fastapi.encoders import jsonable_encoder
from services.bramhastra.models.fcl_freight_rate_request_statistics import (
    FclFreightRateRequestStatistic,
)

class Request:
    def __init__(self, params) -> None:
        self.params = params if isinstance(params, dict) else dict(params)

        self.exclude_keys = {
            "rate_request_id",
            "origin_country_id",
            "origin_trade_id",
            "origin_continent_id",
            "destination_country_id",
            "destination_trade_id",
            "destination_continent_id",
            "origin_region_id",
            "destination_region_id",
            "container_size",
            "container_type",
            "commodity",
        }
        self.missing_locations = dict()

        self.set_missing_locations()

    def set_missing_locations(self):
        self.set_pricing_map_zone_ids()

        self.set_missing_location_ids()

        self.params.update(self.missing_locations)

    def set_missing_location_ids(self):
        response = maps.list_locations(
            data={
                "filters": {
                    "id": [
                        self.params.get("origin_port_id"),
                        self.params.get("destination_port_id"),
                    ]
                },
                "includes": {"continent_id": True, "region_id": True, "id": True},
            }
        )
        if "list" in response and len(response["list"]) == 2:
            region_id_mapping = {
                item["id"]: dict(
                    region_id=item["region_id"], continent_id=item["continent_id"]
                )
                for item in response["list"]
            }
            origin = region_id_mapping.get(self.params.get("origin_port_id"))

            destination = region_id_mapping.get(self.params.get("destination_port_id"))

            self.missing_locations["origin_region_id"] = origin.get("region_id")
            self.missing_locations["destination_region_id"] = destination.get(
                "region_id"
            )

            self.missing_locations["origin_continent_id"] = origin.get("continent_id")
            self.missing_locations["destination_continent_id"] = destination.get(
                "continent_id"
            )

    def set_pricing_map_zone_ids(self) -> list:
        ids = [
            self.params.get("origin_port_id"),
            self.params.get("destination_port_id"),
        ]
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
        self.missing_locations[
            "origin_pricing_zone_map_id"
        ] = map_zone_location_mapping.get(self.params.get("origin_port_id"))

        self.missing_locations[
            "destination_pricing_zone_map_id"
        ] = map_zone_location_mapping.get(self.params.get("destination_port_id"))

    def set_new_stats(self) -> int:
        return FclFreightRateRequestStatistic(**self.params).save()

    def set_existing_stats(self) -> None:
        if (
            request := FclFreightRateRequestStatistic.select()
            .where(
                FclFreightRateRequestStatistic.rate_request_id
                == self.params.get("rate_request_id")
            )
            .first()
        ):
            for k, v in self.params.items():
                if k not in self.exclude_keys:
                    setattr(request, k, v)
            request.save()
            return
