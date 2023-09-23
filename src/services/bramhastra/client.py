from clickhouse_driver import Client
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from configs.env import CLICK_DATABASE_HOST, CLICK_DATABASE_PASSWORD
from services.bramhastra.enums import AppEnv
from configs.env import ENVIRONMENT_TYPE
import logging
import time

logger = logging.getLogger("click")
logger.setLevel(logging.DEBUG)


class ClickHouse:
    def __init__(self) -> None:
        self.client = Client(host=CLICK_DATABASE_HOST, password=CLICK_DATABASE_PASSWORD)

    def execute(self, query, parameters=None):
        start_time = time.perf_counter_ns()
        result = self.client.execute(query, parameters, with_column_types=True)
        end_time = time.perf_counter_ns()
        if ENVIRONMENT_TYPE == "shell":
            logger.debug((query, parameters))
            logger.info("Execution Time: %.2f ms" % ((end_time - start_time) / 1e6))
        if result is not None:
            column_names = [column[0] for column in result[1]]
            data = [row for row in result[0]]
            return [dict(zip(column_names, row)) for row in data]


def json_encoder_for_clickhouse(data):
    return jsonable_encoder(
        data, custom_encoder={datetime: lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S")}
    )
