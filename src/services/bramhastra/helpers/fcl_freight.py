from services.bramhastra.clickhouse.connect import get_clickhouse_client
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from database.rails_db import get_connection
from services.bramhastra.enums import Table,ValidityAction
from peewee import Model

class Connection:
    def __init__(self) -> None:
        self.rails_db = get_connection()
        self.clickhouse_client = get_clickhouse_client()


class FclFreightValidity(Connection):
    def __init__(self,rate_id,validity_id) -> None:
        super().__init__()
        self.rate_id = None
        self.validity_id = None
        self.fcl_freight_rate_statistics_identifier = None
        self.set_initial_parameters(rate_id,validity_id)

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
        
    def get_postgres_statistics_rows_by_rate_id(self,state = 1,version = None) -> Model:
        fcl_freight_rate_statistic_query = (
            FclFreightRateStatistic.select()
            .where(
                FclFreightRateStatistic.rate_id
                == self.rate_id,
                FclFreightRateStatistic.state == state
            )
        )
        if version:
            fcl_freight_rate_statistic_query.where(FclFreightRateStatistic.version == version)
            
        return fcl_freight_rate_statistic_query
        

    def set_initial_parameters(self,rate_id,validity_id) -> None:
        self.rate_id = rate_id
        self.validity_id = validity_id
        self.fcl_freight_rate_statistics_identifier = "".join(
            [rate_id, validity_id]
        )
        
    def get_or_create_statistics_current_row(self) -> Model:
        row = self.get_postgres_statistics_current_row_by_identifier()
        if not row:
            row_params = self.get()
            row = self.create_stats(row_params)
        return row
    
    def create_stats(self,create_param) -> Model:
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


class Statistics([FclFreightValidity]):
    def __init__(self, freight) -> None:
        super().__init__({'rate_id': freight.rate_id,'validity_id': freight.validity_id})
        self.freight = freight
    
    def set_formatted_data(self)-> None:
        if self.freight.action == ValidityAction.unchanged.value:
            pass
        elif self.freight.action == ValidityAction.create.value:
            pass
        elif self.freight.action == ValidityAction.update.value:
            self.update_params = None
            
    def insert_stats(self,create_params):
            FclFreightRateStatistic.insert_many(create_params).execute()


class SpotSearch(FclFreight):
    def apply_create_stats(self, statistical_params):
        pass

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
