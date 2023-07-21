from clickhouse_driver import Client

def get_clickhouse_client():
    with Client(host='localhost', password='') as client:
        return client