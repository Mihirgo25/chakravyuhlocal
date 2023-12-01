from services.bramhastra.client import ClickHouse
from libs.json_encoder import json_encoder

from services.bramhastra.models.air_freight_rate_statistic import (
    AirFreightRateStatistic,
)

RATE_COUNT_FILTER_OPTIONS = [
    "origin_airport_id",
    "destination_airport_id",
    "service_provider_id",
]


def get_air_freight_port_pair_count(filters):
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
        f'''SELECT {select} ,COUNT(DISTINCT rate_id) as rate_count 
        FROM brahmastra.{AirFreightRateStatistic._meta.table_name}
        WHERE ({' OR '.join(where)}) AND validity_end >= toDate(now()) GROUP BY {select}'''
    )

    return {"port_pair_rate_count": json_encoder(clickhouse.execute(full_query))}
