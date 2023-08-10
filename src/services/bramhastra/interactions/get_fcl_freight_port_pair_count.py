from services.bramhastra.client import ClickHouse


def get_fcl_freight_port_pair_count(pairs):
    clickhouse = ClickHouse()

    query_conditions = [
        f"(origin_port_id = '{pair.get('origin_port_id')}' AND destination_port_id = '{pair.get('destination_port_id')}')"
        for pair in pairs
    ]

    full_query = (
        "SELECT origin_port_id, destination_port_id, SUM(sign) as rate_count"
        "FROM brahmastra.fcl_freight_rate_statistics "
        f"WHERE {' OR '.join(query_conditions)} "
        "GROUP BY origin_port_id, destination_port_id"
    )
    return {'port_pair_rate_count': clickhouse.execute(full_query)}
