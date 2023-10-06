from services.bramhastra.client import ClickHouse
from services.bramhastra.helpers.fcl_freight_filter_helper import (
    get_direct_indirect_filters,
)
from fastapi.encoders import jsonable_encoder
from math import ceil
from micro_services.client import maps

HEIRARCHY = ["continent", "country", "region", "port"]

LOCATION_KEYS = {
    "destination_port_id",
    "destination_country_id",
    "destination_continent_id",
    "destination_region_id",
}


def get_fcl_freight_map_view_statistics(filters,sort_by,sort_type, page_limit, page):
    clickhouse = ClickHouse()
    
    sort_by = filter_sort(sort_by)

    grouping = set()

    alter_filters_for_map_view(filters, grouping)

    queries = [
        f'SELECT {",".join(grouping)},FLOOR(ABS(AVG(accuracy)),2) as total_accuracy,count(DISTINCT rate_id) as total_rates FROM brahmastra.fcl_freight_rate_statistics'
    ]

    if where := get_direct_indirect_filters(filters):
        queries.append(" WHERE ")
        queries.append(where)
        queries.append("AND accuracy != -1 and accuracy != 0")

    add_group_by_and_order_by(queries, grouping,sort_by,sort_type)
    
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


def add_group_by_and_order_by(queries, grouping,sort_by,sort_type):
    queries.append("GROUP BY")
    queries.append(",".join(grouping))
    queries.append(
        f"ORDER BY {sort_by} {sort_type}"
    )


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
            grouping.add(f"destination_{HEIRARCHY[1]}_id")
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
    
    indices_to_remove = set()

    for index,statistic in enumerate(statistics):
        update_statistic = dict()
        remove = None
        if not statistic:
            continue
        for k, v in statistic.items():
            if k in LOCATION_KEYS:
                remove = k
                location = locations.get(v)
                if location is None:
                    if k == "destination_region_id":
                        indices_to_remove.add(index)
                    continue
                for key, value in location.items():
                    update_statistic[f"{k[:12]}{key}"] = value
        statistic.pop(remove)
        statistic.update(update_statistic)
    
    for index in indices_to_remove:
        del statistics[index]
        
    
def filter_sort(sort_by):
    return 'total_accuracy' if sort_by == 'accuracy' else sort_by
    
