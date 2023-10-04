from datetime import date, timedelta, datetime
from math import ceil
from services.bramhastra.enums import FclFilterTypes, MapsFilter, Status
from micro_services.client import maps
from services.bramhastra.constants import (
    AGGREGATE_FILTER_MAPPING,
)

POSSIBLE_DIRECT_FILTERS = {
    "origin_country_id",
    "origin_port_id",
    "origin_trade_id",
    "origin_continent_id",
    "destination_port_id",
    "destination_country_id",
    "destination_trade_id",
    "destination_continent_id",
    "origin_region_id",
    "destination_region_id",
    "shipping_line_id",
    "service_provider_id",
    "importer_exporter_id",
    "container_size",
    "container_type",
    "commodity",
    "origin_main_port_id",
    "destination_main_port_id",
    "procured_by_id",
    "rate_type",
    "parent_mode",
    "parent_rate_mode",
    "sourced_by_id",
    "procured_by_id",
    "rate_id",
}

POSSIBLE_INDIRECT_FILTERS = {
    "stale_rate",
    "rate_updated_at_less_than",
    "validity_end_greater_than",
    "validity_end_less_than",
    "select_aggregate",
}

COUNT_FILTERS = {"dislikes_count", "checkout_count"}

REQUIRED_FILTERS = {
    "start_date": datetime(1990, 5, 3).date(),
    "end_date": date.today() + timedelta(days=365),
}


def get_direct_indirect_filters(filters, date="time_series"):
    if filters is None:
        return
    for k, v in REQUIRED_FILTERS.items():
        if k not in filters:
            filters[k] = v

    where = []

    if date == FclFilterTypes.validity_range.value:
        get_date_range_filter(where)

    if date == FclFilterTypes.time_series.value:
        get_time_series_filter(where)

    if filters:
        for key, value in filters.items():
            if key in POSSIBLE_DIRECT_FILTERS and value:
                if type(value) == list and value:
                    where.append(f"{key} IN %({key})s")
                elif value:
                    where.append(f"{key} = %({key})s")
            if key in POSSIBLE_INDIRECT_FILTERS and value:
                eval(f"get_{key}_filter(where, value)")
            if key in COUNT_FILTERS:
                where.append(f"{key} != 0")

    if where:
        return " AND ".join(where)


def get_time_series_filter(where):
    where.append("(updated_at >= %(start_date)s AND updated_at <= %(end_date)s)")


def get_date_range_filter(where):
    where.append(
        "((validity_end >= %(start_date)s AND validity_start <= %(start_date)s) OR (validity_start <= %(end_date)s AND validity_end >= %(end_date)s) OR (validity_end <= %(end_date)s AND validity_start >= %(start_date)s))"
    )


def get_rate_updated_at_less_than_filter(where, value=None):
    where.append("rate_updated_at < %(rate_updated_at_less_than)s")


def get_validity_end_greater_than_filter(where, value=None):
    where.append("validity_end > %(validity_end_greater_than)s")


def get_validity_end_less_than_filter(where, value=None):
    where.append("validity_end < %(validity_end_less_than)s")


def get_stale_rate_filter(where, value=None):
    where.append("checkout_count = 0 AND dislikes_count = 0 AND likes_count = 0")


def get_select_aggregate_filter(where, obj):
    is_multiple = False
    for agg_key in obj.values():
        if agg_key not in AGGREGATE_FILTER_MAPPING:
            continue
        column = AGGREGATE_FILTER_MAPPING[agg_key]["state"]
        value = AGGREGATE_FILTER_MAPPING[agg_key]["value"]
        comparator = AGGREGATE_FILTER_MAPPING[agg_key].get("comparator", "=")
        if not (column and value):
            continue
        if is_multiple:
            where.append(" AND ")
        where.append(f" {column} {comparator} {value} ")
        is_multiple = True


def add_pagination_data(clickhouse, queries, filters, page, page_limit):
    total_count = clickhouse.execute(
        f"SELECT COUNT() as count FROM ({' '.join(queries)})", filters
    )[0]["count"]

    offset = (page - 1) * page_limit
    queries.append(f"LIMIT {page_limit} OFFSET {offset}")
    total_pages = ceil(total_count / page_limit)

    return total_count, total_pages


def set_port_code_filters_and_service_object(filters, location_object):
    origin_port_code = filters.pop(MapsFilter.origin_port_code.value, None)
    destination_port_code = filters.pop(MapsFilter.destination_port_code.value, None)

    locations = maps.list_locations(
        data={
            "filters": {
                "port_code": [origin_port_code, destination_port_code],
                "status": Status.active.value,
            },
            "includes": {
                "id": True,
                "name": True,
                "display_name": True,
                "port_code": True,
            },
        }
    ).get("list", None)

    port_code_to_location_details_mapping = {
        location["port_code"]: location for location in locations
    }

    if origin_port_code:
        location_object["origin_port"] = port_code_to_location_details_mapping.get(
            origin_port_code
        )

        filters["origin_port_id"] = location_object["origin_port"]["id"]

    if destination_port_code:
        location_object["destination_port"] = port_code_to_location_details_mapping.get(
            destination_port_code
        )
        filters["destination_port_id"] = location_object["destination_port"]["id"]
