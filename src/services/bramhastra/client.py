from clickhouse_driver import Client
from fastapi.encoders import jsonable_encoder
from datetime import datetime

class ClickHouse:
    def __init__(self) -> None:
        self.client = Client(host="localhost", password="")
        
    def execute(self, query, parameters=None):
        if result := self.client.execute(query, parameters, with_column_types=True):
            column_names = [column[0] for column in result[1]]
            data = [row for row in result[0]]
            return [dict(zip(column_names, row)) for row in data]


def json_encoder_for_clickhouse(data):
    return jsonable_encoder(
        data, custom_encoder={datetime: lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S")}
    )
