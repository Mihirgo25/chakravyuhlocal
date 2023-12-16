from services.air_freight_rate.models.air_freight_location_cluster_mapping import (
    AirFreightLocationClusterMapping,
    AirFreightLocationCluster,
)
from micro_services.client import maps
from fastapi.encoders import jsonable_encoder
from services.bramhastra.models.air_freight_rate_request_statistics import (
    AirFreightRateRequestStatistic,
)
from services.bramhastra.enums import RequestAction, Status
from services.bramhastra.models.air_freight_action import AirFreightAction
from services.bramhastra.enums import RateRequestState

import uuid

EXCLUDE_UPDATE_KEYS = {
    AirFreightRateRequestStatistic.rate_request_id.name,
    AirFreightRateRequestStatistic.origin_continent_id.name,
    AirFreightRateRequestStatistic.destination_continent_id.name,
    AirFreightRateRequestStatistic.origin_country_id.name,
    AirFreightRateRequestStatistic.destination_country_id.name,
    AirFreightRateRequestStatistic.origin_trade_id.name,
    AirFreightRateRequestStatistic.destination_trade_id.name,
    AirFreightRateRequestStatistic.origin_airport_id.name,
    AirFreightRateRequestStatistic.destination_airport_id.name,
    AirFreightRateRequestStatistic.origin_pricing_zone_map_id.name,
    AirFreightRateRequestStatistic.destination_pricing_zone_map_id.name,
    AirFreightRateRequestStatistic.commodity.name,
    AirFreightRateRequestStatistic.commodity_type.name,
    AirFreightRateRequestStatistic.commodity_subtype.name,
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
                        self.params.get("origin_airport_id"),
                        self.params.get("destination_airport_id"),
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
            origin = region_id_mapping.get(self.params.get("origin_airport_id"))

            destination = region_id_mapping.get(self.params.get("destination_airport_id"))

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
            self.params.get("origin_airport_id"),
            self.params.get("destination_airport_id"),
        ]
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
        self.missing_locations[
            "origin_pricing_zone_map_id"
        ] = map_zone_location_mapping.get(self.params.get("origin_airport_id"))

        self.missing_locations[
            "destination_pricing_zone_map_id"
        ] = map_zone_location_mapping.get(self.params.get("destination_airport_id"))

    def create(self) -> int:
        return AirFreightRateRequestStatistic(**self.params).save()

    def update_air_freight_action(self, action) -> None:
        Air_freight_action = self.get_air_freight_action()
        if Air_freight_action is None:
            return
        if action == RequestAction.create.name:
            setattr(
                Air_freight_action,
                AirFreightAction.rate_request_state.name,
                RateRequestState.created.name,
            )
            rate_requested_ids = getattr(
                Air_freight_action, AirFreightAction.rate_requested_ids.name
            )
            if not rate_requested_ids:
                rate_requested_ids = [
                    self.params.get(AirFreightRateRequestStatistic.rate_request_id.name)
                ]
            else:
                rate_requested_ids.append(
                    self.params.get(AirFreightRateRequestStatistic.rate_request_id.name)
                )
            rate_requested_ids = [
                uuid.UUID(uuid_str) if isinstance(uuid_str, str) else uuid_str
                for uuid_str in rate_requested_ids
            ]
            setattr(
                Air_freight_action,
                AirFreightAction.rate_requested_ids.name,
                rate_requested_ids,
            )
        else:
            if self.params.get("status") == Status.inactive.value:
                setattr(
                    Air_freight_action,
                    AirFreightAction.rate_request_state.name,
                    RateRequestState.closed.name,
                )
            if self.params.get(AirFreightRateRequestStatistic.is_rate_reverted.name):
                setattr(
                    Air_freight_action,
                    AirFreightAction.rate_request_state.name,
                    RateRequestState.rate_added.name,
                )
        setattr(
            Air_freight_action,
            AirFreightAction.updated_at.name,
            self.params.get(AirFreightRateRequestStatistic.updated_at.name),
        )
        Air_freight_action.save()

    def get_air_freight_action(self):
        return (
            AirFreightAction.select()
            .where(AirFreightAction.spot_search_id == self.params.get("source_id"))
            .first()
        )

    def update_statistics(self) -> None:
        if (
            request := AirFreightRateRequestStatistic.select()
            .where(
                AirFreightRateRequestStatistic.rate_request_id
                == self.params.get(AirFreightRateRequestStatistic.rate_request_id.name)
            )
            .first()
        ):
            for k, v in self.params.items():
                if k not in EXCLUDE_UPDATE_KEYS:
                    setattr(request, k, v)
            request.save()
