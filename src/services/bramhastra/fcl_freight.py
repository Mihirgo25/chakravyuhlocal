from services.bramhastra.clickhouse.connect import get_clickhouse_client
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from database.rails_db import get_connection
from services.bramhastra.enums import Table
from peewee import Model


class FclFreight:
    def __init__(self, rate_id, validity_id) -> None:
        self.rate_id = (rate_id)
        self.validity_id = validity_id
        self.fcl_freight_rate_statistics_identifier = (
            self.get_clickhouse_fcl_freight_rate_statistics_identifier()
        )
        self.rails_db = get_connection()
        self.clickhouse_client = get_clickhouse_client()
        self.postgres_statistics_current_row = self.get_postgres_statistics_current_row

    def create_statistics_stale_row(self,row) -> Model:
        row.version+=1
        return FclFreightRateStatistic.create(row)

    def get_postgres_statistics_current_row_by_identifier(self) -> Model:
        return (
            FclFreightRateStatistic.select()
            .where(
                FclFreightRateStatistic.identifier
                == self.fcl_freight_rate_statistics_identifier,
                FclFreightRateStatistic.state == 1
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
        
    def get_postgres_statistics_rows_by_rate_id(self) -> Model:
        return (
            FclFreightRateStatistic.select()
            .where(
                FclFreightRateStatistic.rate_id
                == self.rate_id,
                FclFreightRateStatistic.state == 1
            )
        )
        

    def get_clickhouse_fcl_freight_rate_statistics_identifier(self) -> str:
        self.fcl_freight_rate_statistics_identifier = "".join(
            [self.rate_id, self.validity_id]
        )


class Rate(FclFreight):
    def __init__(self, freight) -> None:
        super().__init__(rate_id=freight["id"], validity_id=freight["validity_id"])
        self.freight = freight

    def get_or_create_statistics_current_row(self) -> Model:
        row = self.get_postgres_statistics_current_row_by_identifier()
        if not row:
            row_params = self.get()
            row = self.apply_create_stats(row_params)
        return row

    def apply_create_stats(self, params) -> Model:
        return FclFreightRateStatistic.create(params)

    def apply_update_stats(self, params) -> int:
        return (
            FclFreightRateStatistic.update(*params)
            .where(
                FclFreightRateStatistic.identifier
                == self.fcl_freight_rate_statistics_identifier
            )
            .execute()
        )


class SpotSearch(FclFreight):
    def apply_create_stats(self, statistical_params, params):
        FclFreightRateStatistic.update(statistical_params).where(
            FclFreightRateStatistic.identifier
            == self.fcl_freight_rate_statistics_identifier
        )

    def apply_update_stats(params):
        pass


class Checkout(FclFreight):
    def apply_create_stats(params):
        pass

    def apply_update_stats(params):
        pass


class Quotations(FclFreight):
    def apply_create_stats(params):
        pass

    def apply_update_stats(params):
        pass


class Shipment(FclFreight):
    def apply_create_stats(params):
        pass

    def apply_update_stats(params):
        pass
