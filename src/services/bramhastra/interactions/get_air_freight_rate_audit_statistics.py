from services.bramhastra.client import ClickHouse
from fastapi.encoders import jsonable_encoder
from services.bramhastra.helpers.air_freight_filter_helper import (
    get_direct_indirect_filters,
)
from services.bramhastra.models.air_freight_rate_audit_statistic import AirFreightRateAuditStatistic

def get_air_freight_rate_audit_statistics(filters):
    where = get_direct_indirect_filters(filters)
    response = get_rate(filters, where)
    return {
        "rate_trend": response
    }
    

def get_rate(filters, where):
    clickhouse = ClickHouse()
    queries = [
        f"""SELECT toDate(day) AS day,AVG(standard_price) AS average_price FROM (SELECT arrayJoin(range(toUInt32(validity_start), toUInt32(validity_end) - 1)) AS day,standard_price FROM brahmastra.{AirFreightRateAuditStatistic._meta.table_name}"""
    ]

    if where:
        queries.append(f""" WHERE code = '{filters.get("code","BAS")}' AND """)
        queries.append(where)
        
    queries.append(
        """) WHERE (day <= %(end_date)s) AND (day >= %(start_date)s) GROUP BY day ORDER BY day;"""
    )

    charts = jsonable_encoder(clickhouse.execute(" ".join(queries), filters))

    return charts