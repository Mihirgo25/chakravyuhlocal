from services.bramhastra.client import ClickHouse
from fastapi.encoders import jsonable_encoder
from services.bramhastra.helpers.air_freight_filter_helper import (
    get_direct_indirect_filters,
    add_pagination_data,
)
from micro_services.client import maps
from services.bramhastra.models.air_freight_action import AirFreightAction
from services.bramhastra.enums import AirFilterTypes
from services.bramhastra.models.air_freight_rate_statistic import (
    AirFreightRateStatistic,
)

DEFAULT_PARAMS = {
    "origin_airport_id",
    "destination_airport_id",
    "airline_id",
    "service_provider_id",
    "commodity",
    "commodity_type",
    "commodity_subtype",
    "rate_type",
}

DEFAULT_AGGREGATE_PARAMS = {
    "spot_search_count": "COUNT(DISTINCT spot_search_id)",
    "checkout_count": "SUM(checkout*sign)",
    "bookings_created": "SUM(shipment*sign)",
    "rate_deviation_from_booking_rate": "MAX(ABS(standard_price_diff_from_selected_rate))",
    "standard_price_deviation": "stddevPop(standard_price)",
}

DEFAULT_SELECT_KEYS = {
    "origin_airport_id",
    "destination_airport_id",
}

LOCATION_KEYS = {
    "origin_airport_id",
    "destination_airport_id",
}

DEFAULT_QUERY_TYPE = "default"

ALLOWABLE_QUERY_TYPES = {"default", "average_price", "rates_affected"}


def add_service_objects(statistics):
    location_ids = set()
    airline_ids = set()

    for statistic in statistics:
        for k, v in statistic.items():
            if k in LOCATION_KEYS:
                location_ids.add(v)
            if k == "airline_id":
                airline_ids.add(v)

    airlines = get_airlines(airline_ids)

    locations = get_locations(location_ids)

    for statistic in statistics:
        update_statistic = dict()
        for k, v in statistic.items():
            if k in LOCATION_KEYS:
                location = locations.get(v)
                if not location:
                    continue
                update_statistic[f"{k[:-3]}"] = location
            if k == "airline_id":
                airline = airlines.get(v)
                if not airline:
                    continue
                update_statistic["airline"] = airline
        statistic.update(update_statistic)


def get_airlines(ids):
    if not ids:
        return dict()
    return {
        airline["id"]: airline
        for airline in maps.list_operators(
            dict(
                filters=dict(id=list(ids)),
                page_limit=len(ids),
            )
        )["list"]
    }


def get_locations(ids):
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


def list_air_freight_rate_statistics(
    filters, page_limit, page, is_service_object_required
):
    if (
        "query_type" in filters
        and filters.get("query_type") not in ALLOWABLE_QUERY_TYPES
    ):
        raise ValueError("invalid type")
    return eval(
        f"use_{filters.get('query_type') or DEFAULT_QUERY_TYPE}_filter({filters}, {page_limit}, {page},{is_service_object_required})"
    )


def use_average_price_filter(
    filters, page_limit, page, is_service_object_required
):
    grouping = filters.get("group_by") or DEFAULT_PARAMS

    clickhouse = ClickHouse()

    if not grouping:
        grouping = DEFAULT_SELECT_KEYS.copy()

    select = ",".join(grouping)

    queries = [
        f"""SELECT {select},AVG(standard_price) as average_standard_price, stddevPop(standard_price) as standard_price_deviation FROM brahmastra.{AirFreightRateStatistic._meta.table_name} WHERE sign = 1 AND standard_price > 0 AND is_deleted = False"""
    ]

    if where := get_direct_indirect_filters(filters):
        queries.append("AND")
        queries.append(where)

    queries.append(f"GROUP BY {select}")

    total_count, total_pages = add_pagination_data(
        clickhouse, queries, filters, page, page_limit
    )

    statistics = jsonable_encoder(clickhouse.execute(" ".join(queries), filters))

    if statistics and is_service_object_required:
        add_service_objects(statistics)

    return dict(
        list=statistics,
        page=page,
        page_limit=page_limit,
        total_pages=total_pages,
        total_count=total_count,
    )


def use_rates_affected_filter(
    filters, page_limit, page, is_service_object_required
):
    clickhouse = ClickHouse()
    query = [
        f"""SELECT toUnixTimestamp(DATE(rate_updated_at),'Asia/Tokyo')*1000 AS day,COUNT(*) as rates_count FROM brahmastra.{AirFreightRateStatistic._meta.table_name}"""
    ]
    query.append(
        f"WHERE rate_updated_at >= %(start_date)s AND rate_updated_at <= %(end_date)s AND day > 0 "
    )
    where = get_direct_indirect_filters(filters, date=None)
    if where:
        query.append(f"AND {where}")
    query.append("GROUP BY DATE(rate_updated_at) ORDER BY day ASC")
    return {"list": clickhouse.execute(" ".join(query), filters)}


def use_default_filter(filters, page_limit, page, is_service_object_required):
    clickhouse = ClickHouse()

    select = ",".join(DEFAULT_PARAMS)

    aggregate_select = ",".join(
        [f"{v} AS aggregate_{k}" for k, v in DEFAULT_AGGREGATE_PARAMS.items()]
    )

    queries = [
        f"""SELECT {select},{aggregate_select} from brahmastra.{AirFreightAction._meta.table_name}"""
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
        add_service_objects(statistics)

    return dict(
        list=statistics,
        page=page,
        page_limit=page_limit,
        total_pages=total_pages,
        total_count=total_count,
    )
