from services.bramhastra.client import ClickHouse
from libs.json_encoder import json_encoder

valid_filter_keys = ["origin_port_id", "destination_port_id", "service_provider_id"]


def get_fcl_freight_port_pair_count(filters):
    clickhouse = ClickHouse()
    select_columns = set()
    query_conditions = []
    for filter in filters:
        conditions = []

        for key, value in filter.items():
            if key in valid_filter_keys:
                conditions.append(f"{key} = '{value}'")
                select_columns.add(key)

        if conditions:
            query_conditions.append(" AND ".join(conditions))
    select_columns_str = ", ".join(select_columns)
    full_query = (
        f"SELECT {select_columns_str} ,SUM(sign) as rate_count "
        "FROM brahmastra.fcl_freight_rate_statistics "
        f"WHERE {' OR '.join(query_conditions)} "
        f"GROUP BY {select_columns_str} "
    )

    return {"port_pair_rate_count": json_encoder(clickhouse.execute(full_query))}
