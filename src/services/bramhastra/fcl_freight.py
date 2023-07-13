from services.bramhastra.clickhouse.connect import get_clickhouse_client
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from database.rails_db import get_connection
from services.bramhastra.enums import Table
from peewee import Model


class FclFreight:
    def __init__(self, rate_id, validity_id) -> None:
        self.rate_id = (rate_id,)
        self.validity_id = validity_id
        self.fcl_freight_rate_statistics_identifier = (
            self.get_clickhouse_fcl_freight_rate_statistics_identifier()
        )
        self.rails_db = get_connection()
        self.clickhouse_client = get_clickhouse_client()
        self.fcl_freight_rate_statistic = None

    def create_statistics_stale_row():
        pass

    def get_postgres_statistics_current_row(self) -> Model:
        return (
            FclFreightRateStatistic.select()
            .where(
                FclFreightRateStatistic.identifier
                == self.fcl_freight_rate_statistics_identifier
            )
            .first()
        )

    def get_clickhouse_statistics_current_row(self):
        parameters = {
            "table": Table.fcl_freight_rate_statistics,
            "identifier": self.fcl_freight_rate_statistics_identifier,
        }
        return self.clickhouse_client.command(
            "SELECT * FROM {table:Identifier} WHERE identifier = {identifier:UUID}",
            parameters,
        )

    def get_clickhouse_fcl_freight_rate_statistics_identifier(self) -> str:
        self.fcl_freight_rate_statistics_identifier = "".join(
            [self.rate_id, self.validity_id]
        )


class Rate(FclFreight):
    def apply_create_stats(self, params):
        return FclFreightRateStatistic.create(params)

    def apply_update_stats(self, params):
        return (
            FclFreightRateStatistic.update(*params)
            .where(
                FclFreightRateStatistic.identifier
                == self.fcl_freight_rate_statistics_identifier
            )
            .execute()
        )


class SpotSearch(FclFreight):
    def apply_create_stats(self,statistical_params,params):
        FclFreightRateStatistic.update(statistical_params).where(FclFreightRateStatistic.identifier == self.fcl_freight_rate_statistics_identifier)

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
