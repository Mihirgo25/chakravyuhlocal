from services.bramhastra.client import ClickHouse
from fastapi.encoders import jsonable_encoder
from services.bramhastra.helpers.air_freight_filter_helper import (
    get_direct_indirect_filters,
    add_pagination_data,
)
from micro_services.client import maps
from services.bramhastra.models.air_freight_rate_statistic import (
    AirFreightRateStatistic,
)

DEFAULT_INCUDE_PARAMS = {
    "origin_airport_id",
    "destination_airport_id",
    "airline_id",
    "service_provider_id",
    "cogo_entity_id",
    "commodity",
    "rate_type",
}

DEFAULT_AGGREGATE_PARAMS = {
    "standard_price": "AVG(standard_price)",
    "standard_price_deviation": "stddevPop(standard_price)"
}

DEFAULT_SELECT_KEYS = {
    "origin_airport_id",
    "destination_airport_id",
}

DEFAULT_QUERY_TYPE = "default"

ALLOWABLE_QUERY_TYPES = {"default", "aggregate"}

LOCATION_KEYS = {"origin_airport_id", "destination_airport_id"}


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
    filters, page_limit, page, is_service_object_required, pagination_data_required
):
    if (
        "query_type" in filters
        and filters.get("query_type") not in ALLOWABLE_QUERY_TYPES
    ):
        raise ValueError("invalid type")
    return eval(
        f"use_{filters.get('query_type') or DEFAULT_QUERY_TYPE}_query(filters, page_limit, page,is_service_object_required, pagination_data_required)"
    )


def use_aggregate_query(
    filters, page_limit, page, is_service_object_required, pagination_data_required
):
    clickhouse = ClickHouse()

    select = ",".join(filters.get("select", DEFAULT_SELECT_KEYS))

    aggregate_select = ",".join(
        [
            f"{v} AS {k}"
            for k, v in filters.get(
                "aggregate_select", DEFAULT_AGGREGATE_PARAMS
            ).items()
        ]
    )

    query = [
        f"""SELECT {select},{aggregate_select} from brahmastra.{AirFreightRateStatistic._meta.table_name}"""
    ]

    where = get_direct_indirect_filters(filters)

    if where:
        query.append(f"WHERE {where}")

    query.append(f"GROUP BY {select}")

    response = dict()

    if pagination_data_required:
        response["total_count"], response["total_pages"] = add_pagination_data(
            clickhouse, query, filters, page, page_limit
        )

    statistics = jsonable_encoder(clickhouse.execute(" ".join(query), filters))

    if is_service_object_required:
        add_service_objects(statistics)

    response["list"] = statistics

    return response


def use_default_query(
    filters, page_limit, page, is_service_object_required, pagination_data_required
):
    clickhouse = ClickHouse()

    select = ",".join(DEFAULT_INCUDE_PARAMS)

    queries = [
        f"""SELECT {select},rate_deviation_from_booking_rate from brahmastra.air_freight_rate_statistics"""
    ]

    if where := get_direct_indirect_filters(filters):
        queries.append("WHERE")
        queries.append(where)

    response = dict()

    if pagination_data_required:
        response["total_count"], response["total_pages"] = add_pagination_data(
            clickhouse, queries, filters, page, page_limit
        )

    queries.insert(0, "WITH list AS (")

    queries.append(
        f") SELECT {select},MAX(rate_deviation_from_booking_rate) as deviation FROM list GROUP BY {select}"
    )
    statistics = jsonable_encoder(clickhouse.execute(" ".join(queries), filters))

    if is_service_object_required:
        add_service_objects(statistics)

    response["list"] = statistics

    return response
