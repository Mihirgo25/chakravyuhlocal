from services.bramhastra.helpers.get_fcl_freight_rate_helper import ClickHouse
from services.bramhastra.helpers.filter_helper import get_direct_indirect_filters
from fastapi.encoders import jsonable_encoder
from math import ceil
from micro_services.client import maps

HEIRARCHY = ["continent", "country", "region", "port"]

LOCATION_KEYS = {
    "origin_port_id",
    "origin_country_id",
    "origin_trade_id",
    "origin_continent_id",
    "destination_port_id",
    "destination_country_id",
    "destination_trade_id",
    "destination_continent_id",
    "origin_region_id",
    "destination_region_id",
}


def get_fcl_freight_map_view_statistics(filters, page_limit, page):
    clickhouse = ClickHouse()

    grouping = set()

    alter_filters_for_map_view(filters, grouping)

    queries = [
        f'SELECT {",".join(grouping)},floor(abs(AVG(accuracy)),2) as accuracy FROM brahmastra.fcl_freight_rate_statistics'
    ]

    if where := get_direct_indirect_filters(filters):
        queries.append(" WHERE ")
        queries.append(where)

    get_add_group_and_order_by(queries, grouping)

    total_count, total_pages = add_pagination_data(
        clickhouse, queries, filters, page, page_limit
    )

    statistics = jsonable_encoder(clickhouse.execute(" ".join(queries), filters))
    
    add_location_objects(statistics)

    return dict(
        list = statistics,
        page=page,
        page_limit=page_limit,
        total_pages=total_pages,
        total_count=total_count,
    )


def get_add_group_and_order_by(queries, grouping):
    queries.append("GROUP BY")
    queries.append(",".join(grouping))
    queries.append("ORDER BY accuracy")


def alter_filters_for_map_view(filters, grouping):
    if "origin" in filters:
        origin_key = f"origin_{filters['origin']['type']}_id"
        filters[origin_key] = filters["origin"]["id"]
        grouping.add(origin_key)
        if "destination" in filters:
            destination_index_to_look = min(
                HEIRARCHY.index(filters["destination"]["type"]) + 1, len(HEIRARCHY) - 1
            )
            destination_key = f"destination_{HEIRARCHY[destination_index_to_look]}_id"
            grouping.add(destination_key)
            filters[f"destination_{filters['destination']['type']}_id"] = filters[
                "destination"
            ]["id"]
            filters.pop("destination")
        else:
            grouping.add(f"destination_{filters['origin']['type']}_id")
        filters.pop("origin")


def add_pagination_data(clickhouse, queries, filters, page, page_limit):
    total_count = clickhouse.execute(
        f"SELECT COUNT() as count FROM ({' '.join(queries)})", filters
    )[0]["count"]

    offset = (page - 1) * page_limit
    queries.append(f"LIMIT {page_limit} OFFSET {offset}")
    total_pages = ceil(total_count / page_limit)

    return total_count, total_pages


def add_location_objects(statistics):
    
    location_ids = list({v for statistic in statistics for k, v in statistic.items() if k in LOCATION_KEYS})
    
    locations = {
        location["id"]: location
        for location in maps.list_locations(
            dict(
                filters=dict(id=location_ids),
                includes=dict(id=True, name=True,type = True,latitude = True,longitude = True),
                page_limit=len(location_ids),
            )
        )["list"]
    }

    for statistic in statistics:
        update_statistic = dict()
        for k, v in statistic.items():
            if k in LOCATION_KEYS:
                update_statistic[k[:-3]] = locations.get(v)

        statistic.update(update_statistic)