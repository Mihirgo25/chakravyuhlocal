import clickhouse_connect

def get_clickhouse_client():
    with clickhouse_connect.get_client(host='localhost', username='default', password='') as client:
        return client