from services.fcl_freight_rate.models.fcl_freight_location_cluster_mapping import (
    FclFreightLocationClusterMapping,
    FclFreightLocationCluster,
)
from micro_services.client import maps
from fastapi.encoders import jsonable_encoder
from services.bramhastra.models.fcl_freight_rate_request_statistics import (
    FclFreightRateRequestStatistic,
)
from services.bramhastra.enums import RequestAction, Status
from services.bramhastra.models.fcl_freight_action import FclFreightAction
from services.bramhastra.enums import RateRequestState

import uuid

EXCLUDE_UPDATE_KEYS = {
    FclFreightRateRequestStatistic.rate_request_id.name,
    FclFreightRateRequestStatistic.origin_continent_id.name,
    FclFreightRateRequestStatistic.destination_continent_id.name,
    FclFreightRateRequestStatistic.origin_country_id.name,
    FclFreightRateRequestStatistic.destination_country_id.name,
    FclFreightRateRequestStatistic.origin_trade_id.name,
    FclFreightRateRequestStatistic.destination_trade_id.name,
    FclFreightRateRequestStatistic.origin_port_id.name,
    FclFreightRateRequestStatistic.destination_port_id.name,
    FclFreightRateRequestStatistic.origin_pricing_zone_map_id.name,
    FclFreightRateRequestStatistic.destination_pricing_zone_map_id.name,
    FclFreightRateRequestStatistic.container_size.name,
    FclFreightRateRequestStatistic.containers_count.name,
    FclFreightRateRequestStatistic.commodity.name,
}


class Request:
    def __init__(self, params) -> None:
        self.params = params if isinstance(params, dict) else dict(params)

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

    def create(self) -> int:
        return FclFreightRateRequestStatistic(**self.params).save()

    def update_fcl_freight_action(self, action) -> None:
        fcl_freight_action = self.get_fcl_freight_action()
        if fcl_freight_action is None:
            return
        if action == RequestAction.create.name:
            setattr(
                fcl_freight_action,
                FclFreightAction.rate_request_state.name,
                RateRequestState.created.name,
            )
            rate_requested_ids = getattr(
                fcl_freight_action, FclFreightAction.rate_requested_ids.name
            )
            if not rate_requested_ids:
                rate_requested_ids = [
                    self.params.get(FclFreightRateRequestStatistic.rate_request_id.name)
                ]
            else:
                rate_requested_ids.append(
                    self.params.get(FclFreightRateRequestStatistic.rate_request_id.name)
                )
            rate_requested_ids = [
                uuid.UUID(uuid_str) if isinstance(uuid_str, str) else uuid_str
                for uuid_str in rate_requested_ids
            ]
            setattr(
                fcl_freight_action,
                FclFreightAction.rate_requested_ids.name,
                rate_requested_ids,
            )
        else:
            if self.params.get("status") == Status.inactive.value:
                setattr(
                    fcl_freight_action,
                    FclFreightAction.rate_request_state.name,
                    RateRequestState.closed.name,
                )
            if self.params.get(FclFreightRateRequestStatistic.is_rate_reverted.name):
                setattr(
                    fcl_freight_action,
                    FclFreightAction.rate_request_state.name,
                    RateRequestState.rate_added.name,
                )
        setattr(
            fcl_freight_action,
            FclFreightAction.updated_at.name,
            self.params.get(FclFreightRateRequestStatistic.updated_at.name),
        )
        fcl_freight_action.save()

    def get_fcl_freight_action(self):
        return (
            FclFreightAction.select()
            .where(FclFreightAction.spot_search_id == self.params.get("source_id"))
            .first()
        )

    def update_statistics(self) -> None:
        if (
            request := FclFreightRateRequestStatistic.select()
            .where(
                FclFreightRateRequestStatistic.rate_request_id
                == self.params.get(FclFreightRateRequestStatistic.rate_request_id.name)
            )
            .first()
        ):
            for k, v in self.params.items():
                if k not in EXCLUDE_UPDATE_KEYS:
                    setattr(request, k, v)
            request.save()
