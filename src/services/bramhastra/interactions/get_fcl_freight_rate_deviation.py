from services.bramhastra.client import ClickHouse
from services.bramhastra.helpers.fcl_freight_filter_helper import (
    get_direct_indirect_filters,
)
from fastapi.encoders import jsonable_encoder
from math import ceil
from micro_services.client import maps

GROUPING_KEYS = {
    "origin_port_id",
    "origin_region_id",
    "origin_continent_id",
    "origin_trade_id",
    "service_provider_id",
    "shipping_line_id"
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


def get_fcl_freight_map_view_statistics(filters,sort_by,sort_type, page_limit, page):
    clickhouse = ClickHouse()

    grouping = set()
    
    for k in GROUPING_KEYS:
        if k in filters:
            grouping.add(k)

    queries = [
        f'SELECT {",".join(grouping)},MAX(standard_price) AS max_price,MIN(standard_price) as min_price,MAX(standard_price) - MIN(standard_price) as difference FROM brahmastra.fcl_freight_rate_statistics'
    ]

    if where := get_direct_indirect_filters(filters):
        queries.append(" WHERE ")
        queries.append(where)

    get_add_group_and_order_by(queries, grouping,sort_by,sort_type)
    
    total_count, total_pages = add_pagination_data(
        clickhouse, queries, filters, page, page_limit
    )
    statistics = jsonable_encoder(clickhouse.execute(" ".join(queries), filters))

    if statistics:
        add_location_objects(statistics)

    return dict(
        list=statistics,
        page=page,
        page_limit=page_limit,
        total_pages=total_pages,
        total_count=total_count,
    )


def get_add_group_and_order_by(queries, grouping,sort_by,sort_type):
    queries.append("GROUP BY")
    queries.append(",".join(grouping))
    queries.append(
        f"ORDER BY {sort_by} {sort_type}"
    )


def add_pagination_data(clickhouse, queries, filters, page, page_limit):
    total_count = clickhouse.execute(
        f"SELECT COUNT() as count FROM ({' '.join(queries)})", filters
    )[0]["count"]

    offset = (page - 1) * page_limit
    queries.append(f"LIMIT {page_limit} OFFSET {offset}")
    total_pages = ceil(total_count / page_limit)

    return total_count, total_pages


def add_location_objects(statistics):
    location_ids = list(
        {
            v
            for statistic in statistics
            for k, v in statistic.items()
            if k in LOCATION_KEYS
        }
    )

    if not location_ids:
        return

    locations = {
        location["id"]: location
        for location in maps.list_locations(
            dict(
                filters=dict(id=location_ids),
                includes=dict(
                    id=True, name=True, type=True, latitude=True, longitude=True
                ),
                page_limit=len(location_ids),
            )
        )["list"]
    }

    for statistic in statistics:
        update_statistic = dict()
        remove = None
        if not statistic:
            continue
        for k, v in statistic.items():
            if k in LOCATION_KEYS:
                remove = k
                location = locations.get(v)
                if location is None:
                    continue
                for key, value in location.items():
                    update_statistic[f"{k[:12]}{key}"] = value
        statistic.pop(remove)
        statistic.update(update_statistic)
    
