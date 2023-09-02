from services.bramhastra.client import ClickHouse
from fastapi.encoders import jsonable_encoder
from services.bramhastra.helpers.fcl_freight_filter_helper import (
    get_direct_indirect_filters,
    add_pagination_data,
)
from micro_services.client import maps

DEFAULT_PARAMS = {
    "origin_port_id",
    "destination_port_id",
    "origin_main_port_id",
    "destination_main_port_id",
    "shipping_line_id",
    "service_provider_id",
    "cogo_entity_id",
    "container_size",
    "container_type",
    "commodity",
    "rate_type",
}

DEFAULT_AGGREGATE_PARAMS = {
    "spot_search_count": "SUM(spot_search_count)",
    "checkout_count": "SUM(checkout_count)",
    "bookings_created": "SUM(bookings_created)",
    "rate_deviation_from_booking_rate": "MAX(ABS(rate_deviation_from_booking_rate))",
}

DEFAULT_SELECT_KEYS = {
    "origin_port_id",
    "destination_port_id",
}

LOCATION_KEYS = {
    "origin_port_id",
    "destination_port_id",
    "origin_main_port_id",
    "destination_main_port_id",
}

DEFAULT_QUERY_TYPE = "default"

ALLOWABLE_QUERY_TYPES = {"default", "average_price"}


async def add_service_objects(statistics):
    location_ids = set()
    shipping_line_ids = set()

    for statistic in statistics:
        for k, v in statistic.items():
            if k in LOCATION_KEYS:
                location_ids.add(v)
            if k == "shipping_line_id":
                shipping_line_ids.add(v)

    shipping_lines = await get_shipping_lines(shipping_line_ids)

    locations = await get_locations(location_ids)

    for statistic in statistics:
        update_statistic = dict()
        for k, v in statistic.items():
            if k in LOCATION_KEYS:
                location = locations.get(v)
                if not location:
                    continue
                update_statistic[f"{k[:-3]}"] = location
            if k == "shipping_line_id":
                shipping_line = shipping_lines.get(v)
                if not shipping_line:
                    continue
                update_statistic["shipping_line"] = shipping_line
        statistic.update(update_statistic)


async def get_shipping_lines(ids):
    if not ids:
        return dict()
    return {
        shipping_line["id"]: shipping_line
        for shipping_line in maps.list_operators(
            dict(
                filters=dict(id=list(ids)),
                page_limit=len(ids),
            )
        )["list"]
    }


async def get_locations(ids):
    if not ids:
        return dict()
    return {
        location["id"]: location
        for location in maps.list_locations(
            dict(
                filters=dict(id=list(ids)),
                includes=dict(id=True, name=True, port_code=True),
                page_limit=len(ids),
            )
        )["list"]
    }


async def list_fcl_freight_rate_statistics(
    filters, page_limit, page, is_service_object_required
):
    if (
        "query_type" in filters
        and filters.get("query_type") not in ALLOWABLE_QUERY_TYPES
    ):
        raise ValueError("invalid type")
    return await eval(
        f"use_{filters.get('query_type') or DEFAULT_QUERY_TYPE}_filter(filters, page_limit, page,is_service_object_required)"
    )


async def use_average_price_filter(
    filters, page_limit, page, is_service_object_required
):
    clickhouse = ClickHouse()

    grouping = {k for k in DEFAULT_PARAMS if k in filters}

    if not grouping:
        grouping = DEFAULT_SELECT_KEYS.copy()

    select = ",".join(grouping)

    queries = [
        f"SELECT {select},AVG(standard_price) as average_standard_price FROM brahmastra.fcl_freight_rate_statistics"
    ]

    if where := get_direct_indirect_filters(filters):
        queries.append("WHERE")
        queries.append(where)

    queries.append(f"GROUP BY {select}")

    total_count, total_pages = add_pagination_data(
        clickhouse, queries, filters, page, page_limit
    )

    statistics = jsonable_encoder(clickhouse.execute(" ".join(queries), filters))

    if statistics and is_service_object_required:
        await add_service_objects(statistics)

    return dict(
        list=statistics,
        page=page,
        page_limit=page_limit,
        total_pages=total_pages,
        total_count=total_count,
    )


async def use_default_filter(filters, page_limit, page, is_service_object_required):
    clickhouse = ClickHouse()

    select = ",".join(DEFAULT_PARAMS)

    aggregate_select = ",".join(
        [f"{v} AS aggregate_{k}" for k, v in DEFAULT_AGGREGATE_PARAMS.items()]
    )

    queries = [
        f"""SELECT {select},{aggregate_select} from brahmastra.fcl_freight_rate_statistics"""
    ]

    if where := get_direct_indirect_filters(filters):
        queries.append("WHERE")
        queries.append(where)

    queries.append(f"GROUP BY {select}")
    
    total_count, total_pages = add_pagination_data(
        clickhouse, queries, filters, page, page_limit
    )

    statistics = jsonable_encoder(clickhouse.execute(" ".join(queries), filters))

    if statistics and is_service_object_required:
        await add_service_objects(statistics)

    return dict(
        list=statistics,
        page=page,
        page_limit=page_limit,
        total_pages=total_pages,
        total_count=total_count,
    )
