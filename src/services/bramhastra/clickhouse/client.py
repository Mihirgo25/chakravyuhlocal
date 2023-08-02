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


def get_clickhouse_rows_with_column_names(result):
    rows = result.result_rows
    columns = result.column_names
    data = []
    for row in rows:
        decoded_row = []
        for value in row:
            if isinstance(value, bytes):
                decoded_value = value.decode("utf-8").replace("\x00", "")
            else:
                decoded_value = value
            decoded_row.append(decoded_value)
        data.append(dict(zip(columns, decoded_row)))
    return data
