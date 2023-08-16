from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from services.bramhastra.models.feedback_fcl_freight_rate_statistic import (
    FeedbackFclFreightRateStatistic,
)
from services.bramhastra.models.shipment_fcl_freight_rate_statistic import (
    ShipmentFclFreightRateStatistic,
)
from services.bramhastra.models.spot_search_fcl_freight_rate_statistic import (
    SpotSearchFclFreightRateStatistic,
)
from services.bramhastra.models.fcl_freight_rate_request_statistics import (
    FclFreightRateRequestStatistic,
)
from services.bramhastra.client import ClickHouse
from services.bramhastra.client import (
    json_encoder_for_clickhouse,
)
import peewee
from playhouse.postgres_ext import ServerSide
from playhouse.shortcuts import model_to_dict


"""
Info:
Brahmastra is a tool used to send statistics to ClickHouse for analytical queries.

Code:
Brahmastra(models).used_by(arjun=True)

Options:
If models are not send it will run for all available models present in the clickhouse system
If `arjun` is not used, old duplicate entries won't be cleared. We recommend using `arjun` to clear these entries once in a while for better performance.
"""


class Brahmastra:
    def __init__(self, models: list[peewee.Model] = None) -> None:
        self.models = models or [
            FclFreightRateStatistic,
            FeedbackFclFreightRateStatistic,
            ShipmentFclFreightRateStatistic,
            SpotSearchFclFreightRateStatistic,
            FclFreightRateRequestStatistic,
        ]
        self.__clickhouse = ClickHouse().client

    def __optimize_and_send_data_to_stale_tables(self, model: peewee.Model):
        query = f"""
        INSERT INTO brahmastra.stale_{model._meta.table_name} SETTINGS async_insert=1, wait_for_async_insert=1 
        WITH LatestVersions AS (
            SELECT id,version,
            ROW_NUMBER() OVER (PARTITION BY id ORDER BY version DESC) AS row_num
            FROM
            brahmastra.{model._meta.table_name}
        )
        SELECT * FROM brahmastra.{model._meta.table_name} WHERE (id, version) NOT IN (
        SELECT id,version
        FROM LatestVersions
        WHERE row_num = 1)"""
        self.__clickhouse.execute(query)
        self.__clickhouse.execute(f"OPTIMIZE TABLE brahmastra.{model._meta.table_name}")

    def __build_query_and_insert_to_clickhouse(self, model: peewee.Model):
        data = json_encoder_for_clickhouse(list(model.select().dicts()))

        query = f"INSERT INTO brahmastra.{model._meta.table_name} SETTINGS async_insert=1, wait_for_async_insert=1 VALUES"

        columns = model._meta.fields

        values = []

        for d in ServerSide(model.select()):
            value = []
            d = json_encoder_for_clickhouse(model_to_dict(d))
            for k, v in d.items():
                if v is None:
                    value.append("DEFAULT")
                elif (
                    isinstance(columns[k], peewee.UUIDField)
                    or isinstance(columns[k], peewee.TextField)
                    or isinstance(columns[k], peewee.CharField)
                    or isinstance(columns[k], peewee.DateTimeField)
                ):
                    value.append(f"'{v}'")
                elif isinstance(columns[k], peewee.BooleanField):
                    value.append("true" if v else "false")
                else:
                    value.append(f"{v}")
            values.append(f"({','.join(value)})")

        if values:
            self.__clickhouse.execute(query + ",".join(values))
            model.delete().execute()

    def used_by(self, arjun: bool) -> None:
        for model in self.models:
            self.__build_query_and_insert_to_clickhouse(model)
            if arjun:
                self.__optimize_and_send_data_to_stale_tables(model)
                
            print(f'Done with {model._meta.table_name}')
