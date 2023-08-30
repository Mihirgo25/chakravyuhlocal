from services.bramhastra.client import ClickHouse
from services.bramhastra.helpers.fcl_freight_filter_helper import (
    get_direct_indirect_filters,
)
from fastapi.encoders import jsonable_encoder
from math import ceil
from micro_services.client import maps
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)

SELECT = {
    "origin_port_id",
    "origin_region_id",
    "origin_continent_id",
    "origin_trade_id",
    "destination_port_id",
    "destination_region_id",
    "destination_continent_id",
    "destination_trade_id",
    "service_provider_id",
    "shipping_line_id",
}

LOCATION_KEYS = {
    "origin_port_id",
    "origin_region_id",
    "origin_continent_id",
    "origin_trade_id",
    "destination_port_id",
    "destination_region_id",
    "destination_continent_id",
    "destination_trade_id",
}

DEFAULT_SELECT_KEYS = {"service_provider_id"}


def get_fcl_freight_deviation(filters, page_limit, page):
    clickhouse = ClickHouse()

    grouping = set()

    for k in SELECT:
        if k in filters:
            grouping.add(k)

    if not grouping:
        grouping = DEFAULT_SELECT_KEYS.copy()

    subquery = [
        f"WITH AVERAGE AS (SELECT AVG(standard_price) AS average_price,count(validity_id) AS validity_count FROM brahmastra.fcl_freight_rate_statistics"
    ]

    queries = [
        f',NORMAL AS (SELECT {",".join(grouping)},AVG(standard_price) as price FROM brahmastra.{FclFreightRateStatistic._meta.table_name}'
    ]

    final_query = [
        f"SELECT {','.join(grouping)}, SQRT(POW(price - AVERAGE.average_price,2)/AVERAGE.validity_count + 1) AS deviation FROM NORMAL,AVERAGE"
    ]

    if where := get_direct_indirect_filters(filters):
        subquery.append(" WHERE ")
        subquery.append(where)
        queries.append(" WHERE ")
        queries.append(where)

    get_add_group_and_order_by(final_query, subquery, queries, grouping)

    queries = subquery + queries + final_query

    total_count, total_pages = add_pagination_data(
        clickhouse, queries, filters, page, page_limit
    )
    statistics = jsonable_encoder(clickhouse.execute(" ".join(queries), filters))

    return dict(
        list=statistics,
        page=page,
        page_limit=page_limit,
        total_pages=total_pages,
        total_count=total_count,
    )


def get_add_group_and_order_by(final_query, subquery, queries, grouping):
    queries.append("GROUP BY")
    queries.append(",".join(grouping))
    queries.append(")")
    grouping.remove("service_provider_id")
    if grouping:
        subquery.append("GROUP BY")
        subquery.append(",".join(grouping))
    subquery.append(")")

    final_query.append(f"ORDER BY deviation ASC")


def add_pagination_data(clickhouse, queries, filters, page, page_limit):
    total_count = clickhouse.execute(
        f"SELECT COUNT() as count FROM ({' '.join(queries)})", filters
    )[0]["count"]

    offset = (page - 1) * page_limit
    queries.append(f"LIMIT {page_limit} OFFSET {offset}")
    total_pages = ceil(total_count / page_limit)

    return total_count, total_pages
