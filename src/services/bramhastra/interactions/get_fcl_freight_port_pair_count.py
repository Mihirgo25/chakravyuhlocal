from services.bramhastra.client import ClickHouse
from libs.json_encoder import json_encoder

RATE_COUNT_FILTER_OPTIONS = [
    "origin_port_id",
    "destination_port_id",
    "service_provider_id",
]


def get_fcl_freight_port_pair_count(filters):
    clickhouse = ClickHouse()
    select_columns = set()
    where = []
    for filter in filters:
        conditions = []

        for key, value in filter.items():
            if key in RATE_COUNT_FILTER_OPTIONS:
                if isinstance(value, list):
                    value_str = ", ".join([f"'{v}'" for v in value if v])
                    conditions.append(f"{key} IN ({value_str})")
                elif isinstance(value, str):
                    conditions.append(f"{key} = '{value}'")
                select_columns.add(key)

        if conditions:
            where.append(" AND ".join(conditions))
    select = ", ".join(select_columns)
    full_query = (
        f"SELECT {select} ,COUNT(DISTINCT rate_id) as rate_count "
        "FROM brahmastra.fcl_freight_rate_statistics "
        f"WHERE {' OR '.join(where)} "
        f"GROUP BY {select} "
    )

    return {"port_pair_rate_count": json_encoder(clickhouse.execute(full_query))}
