from services.bramhastra.client import ClickHouse
from fastapi.encoders import jsonable_encoder

def get_fcl_freight_rate_for_port_pair(pairs):
    clickhouse = ClickHouse()
    origin_destination_pairs = pairs
    query_conditions = []
    for origin_id, destination_id in origin_destination_pairs:
        condition = f"(origin_port_id = '{origin_id}' AND destination_port_id = '{destination_id}')"
        query_conditions.append(condition)

    full_query = (
    "SELECT origin_port_id, destination_port_id, COUNT(rate_id) "
    "FROM brahmastra.fcl_freight_rate_statistics "
    f"WHERE {' OR '.join(query_conditions)} "
    "GROUP BY origin_port_id, destination_port_id"
)
    return jsonable_encoder(clickhouse.execute(full_query))
