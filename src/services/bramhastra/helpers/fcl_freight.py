from services.bramhastra.clickhouse.connect import get_clickhouse_client
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from database.rails_db import get_connection
from services.bramhastra.enums import Table, ValidityAction
from peewee import Model
from services.fcl_freight_rate.models.fcl_freight_location_cluster_mapping import (
    FclFreightLocationClusterMapping,
    FclFreightLocationCluster,
)
from peewee import Case
from micro_services.client import maps
from fastapi.encoders import jsonable_encoder


class Connection:
    def __init__(self) -> None:
        self.rails_db = get_connection()
        self.clickhouse_client = get_clickhouse_client()


class FclFreightValidity(Connection):
    def __init__(self, rate_id, validity_id, schedule_type, payment_term) -> None:
        super().__init__()
        self.rate_id = None
        self.validity_id = None
        self.fcl_freight_rate_statistics_identifier = None
        self.set_identifier_details(rate_id, validity_id, schedule_type, payment_term)

    def create_statistics_stale_row(self, row) -> Model:
        row.version += 1
        return FclFreightRateStatistic.create(row)

    def get_postgres_statistics_current_row_by_identifier(self) -> Model:
        return (
            FclFreightRateStatistic.select()
            .where(
                FclFreightRateStatistic.identifier
                == self.fcl_freight_rate_statistics_identifier,
                FclFreightRateStatistic.state == 1,
            )
            .first()
        )

    def get_clickhouse_statistics_current_row_by_identifier(self) -> dict:
        parameters = {
            "table": Table.fcl_freight_rate_statistics,
            "identifier": self.fcl_freight_rate_statistics_identifier,
        }
        if row := self.clickhouse_client.command(
            "SELECT * FROM {table:Identifier} WHERE identifier = {identifier:UUID} FINAL",
            parameters,
        ):
            return row

    def get_clickhouse_statistics_rows_by_rate_id(self) -> dict:
        parameters = {
            "table": Table.fcl_freight_rate_statistics,
            "identifier": self.rate_id,
        }
        if row := self.clickhouse_client.command(
            "SELECT * FROM {table:Identifier} WHERE rate_id = {identifier:UUID} FINAL",
            parameters,
        ):
            return row

    def get_postgres_statistics_rows_by_rate_id(self, state=1, version=None) -> Model:
        fcl_freight_rate_statistic_query = FclFreightRateStatistic.select().where(
            FclFreightRateStatistic.rate_id == self.rate_id,
            FclFreightRateStatistic.state == state,
        )
        if version:
            fcl_freight_rate_statistic_query.where(
                FclFreightRateStatistic.version == version
            )

        return fcl_freight_rate_statistic_query

    def set_identifier_details(
        self, rate_id, validity_id, schedule_type, payment_term
    ) -> None:
        self.rate_id = rate_id
        self.validity_id = validity_id
        self.fcl_freight_rate_statistics_identifier = "".join(
            [rate_id, validity_id, schedule_type, payment_term]
        )

    def get_or_create_statistics_current_row(self) -> Model:
        row = self.get_postgres_statistics_current_row_by_identifier()
        if not row:
            row_params = self.get()
            row = self.create_stats(row_params)
        return row

    def create_stats(self, create_param) -> Model:
        return FclFreightRateStatistic.create(create_param)

    def update_stats(self, params) -> int:
        return (
            FclFreightRateStatistic.update(*params)
            .where(
                FclFreightRateStatistic.identifier
                == self.fcl_freight_rate_statistics_identifier
            )
            .execute()
        )


class Rate:
    def __init__(self, freight) -> None:
        self.freight = freight
        self.params = []
        # ports set are main ports
        self.origin_port_id = None
        self.destination_port_id = None
        self.origin_pricing_zone_map_id = None
        self.destination_pricing_zone_map_id = None
        self.origin_region_id = None
        self.destination_region_id = None
        self.set_non_existing_location_details()

    def set_new_stats(self) -> int:
        return FclFreightRateStatistic.insert_many(self.params).execute()

    def set_existing_stats(self) -> None:
        for validity in self.freight.valditiies:
            if validity.action == ValidityAction.create.value:
                pass
            elif validity.action == ValidityAction.update.value:
                pass
            elif validity.action == ValidityAction.unchanged.value:
                continue

    def set_non_existing_location_details(self) -> None:
        self.origin_port_id = (
            self.freight.origin_port_id
            if not self.freight.origin_main_port_id
            else self.freight.origin_main_port_id
        )
        self.destination_port_id = (
            self.freight.destination_port_id
            if not self.freight.destination_main_port_id
            else self.freight.destination_main_port_id
        )

        (
            self.origin_pricing_zone_map_id,
            self.destination_pricing_zone_map_id,
        ) = self.get_pricing_map_zone_ids(self.origin_port_id, self.destination_port_id)
        self.origin_region_id, self.destination_region_id = self.get_region_ids(
            self.origin_port_id, self.destination_port_id
        )

    def set_formatted_data(self) -> None:
        freight = self.freight.dict(exclude={"validities"})

        for validity in self.freight.validities:
            param = freight.copy()
            param.update(validity.dict(exclude={"action"}))
            param["identifier"] = "".join(
                [
                    param["rate_id"],
                    param["validity_id"],
                    param["schedule_type"],
                    param["payment_term"],
                ]
            )
            param["origin_pricing_zone_map_id"] = self.origin_pricing_zone_map_id
            param[
                "destination_pricing_zone_map_id"
            ] = self.destination_pricing_zone_map_id
            param["origin_region_id"] = self.origin_region_id
            param["destination_region_id"] = self.destination_region_id
            param["last_action"] = validity.action
            self.params.append(param)

    def get_pricing_map_zone_ids(self, origin_port_id, destination_port_id) -> list:
        query = (
            FclFreightLocationCluster.select(
                FclFreightLocationClusterMapping.location_id,
                FclFreightLocationCluster.map_zone_id,
            )
            .join(FclFreightLocationClusterMapping)
            .where(
                FclFreightLocationClusterMapping.location_id.in_(
                    [origin_port_id, destination_port_id]
                )
            )
        )
        map_zone_location_mapping = jsonable_encoder(
            {item["location_id"]: item["map_zone_id"] for item in query.dicts()}
        )
        return map_zone_location_mapping.get(
            origin_port_id
        ), map_zone_location_mapping.get(destination_port_id)

    def get_region_ids(self, origin_port_id, destination_port_id):
        response = maps.list_locations(
            data={
                "filters": {"id": [origin_port_id, destination_port_id]},
                "includes": {"region_id": True, "id": True},
            }
        )
        if "list" in response and len(response["list"]) == 2:
            region_id_mapping = {
                item["id"]: item["region_id"] for item in response["list"]
            }
            return region_id_mapping.get(origin_port_id), region_id_mapping.get(
                destination_port_id
            )
        return None, None


class SpotSearch:
    def apply_create_stats(self, statistical_params):
        pass

    def apply_update_stats(params):
        pass


class Checkout(FclFreightValidity):
    def apply_create_stats(params):
        pass

    def apply_update_stats(params):
        pass


class Quotations(FclFreightValidity):
    def apply_create_stats(params):
        pass

    def apply_update_stats(params):
        pass


class Shipment(FclFreightValidity):
    def apply_create_stats(params):
        pass

    def apply_update_stats(params):
        pass
