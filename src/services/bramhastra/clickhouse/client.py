from clickhouse_driver import Client

class ClickHouse:
    def __init__(self) -> None:
        self.clickhouse_client = self.get_clickhouse_client()

    def execute(self, query, parameters=None):
        if result := self.clickhouse_client.execute(
            query, parameters, with_column_types=True
        ):
            column_names = [column[0] for column in result[1]]
            data = [row for row in result[0]]
            return [dict(zip(column_names, row)) for row in data]
        
    def get_clickhouse_client(self):
        with Client(host='localhost', password='') as client:
            return client