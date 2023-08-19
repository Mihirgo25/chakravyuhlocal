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
from services.bramhastra.models.checkout_fcl_freight_rate_statistic import (
    CheckoutFclFreightRateStatistic,
)
from services.bramhastra.client import ClickHouse
import peewee
from configs.env import (
    DATABASE_HOST,
    DATABASE_NAME,
    DATABASE_PASSWORD,
    DATABASE_PORT,
    DATABASE_USER,
)


"""
Info:
Brahmastra is a tool used to send statistics to ClickHouse for analytical queries.

Code:
Brahmastra(models).used_by(arjun=True)

Options:
If models are not send it will run for all available models present in the clickhouse system
If `arjun` is not the user, old duplicate entries won't be cleared. We recommend using `arjun` as user to clear these entries once in a while for better performance.
"""


class Brahmastra:
    def __init__(self, models: list[peewee.Model] = None) -> None:
        self.models = models or [
            FclFreightRateStatistic,
            FeedbackFclFreightRateStatistic,
            ShipmentFclFreightRateStatistic,
            SpotSearchFclFreightRateStatistic,
            FclFreightRateRequestStatistic,
            CheckoutFclFreightRateStatistic,
        ]
        self.__clickhouse = ClickHouse()

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
        fields = ",".join([key for key in model._meta.fields.keys()])
        self.__clickhouse.execute(
            f"INSERT INTO brahmastra.{model._meta.table_name} SELECT {fields} FROM postgresql('{DATABASE_HOST}:{DATABASE_PORT}', '{DATABASE_NAME}', '{model._meta.table_name}', '{DATABASE_USER}', '{DATABASE_PASSWORD}')"
        )
        model.delete().execute()

    def used_by(self, arjun: bool) -> None:
        for model in self.models:
            self.__build_query_and_insert_to_clickhouse(model)
            if arjun:
                self.__optimize_and_send_data_to_stale_tables(model)

            print(f"Done with {model._meta.table_name}")
