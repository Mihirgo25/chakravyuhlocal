from datetime import date, timedelta, datetime
from math import ceil
from services.bramhastra.enums import MapsFilter, Status
from micro_services.client import maps

POSSIBLE_DIRECT_FILTERS = {
    "origin_airport_id",
    "origin_country_id",
    "origin_trade_id",
    "origin_continent_id",
    "destination_airport_id",
    "destination_country_id",
    "destination_trade_id",
    "destination_continent_id",
    "origin_region_id",
    "destination_region_id",
    "airline_id",
    "service_provider_id",
    "importer_exporter_id",
    "commodity_sub_type",
    "commodity_type",
    "commodity",
    "procured_by_id",
    "density_category",
    "operation_type",
    "price_type",
    "shipment_type",
    "stacking_type",
    "rate_type",
    "source",
    "sourced_by_id",
    "procured_by_id",
}

POSSIBLE_INDIRECT_FILTERS = {
    "stale_rate",
    "weight_slabs",
    "chargeable_weight",
    "rate_updated_at_less_than",
    "validity_end_greater_than",
    "validity_end_less_than",
}

COUNT_FILTERS = {"dislikes_count", "checkout_count"}

REQUIRED_FILTERS = {
    "start_date": datetime(1990, 5, 3).date(),
    "end_date": date.today() + timedelta(days=365),
}


def get_direct_indirect_filters(filters):    
    for k, v in REQUIRED_FILTERS.items():
        if k not in filters:
            filters[k] = v
    where = []
    
    get_date_range_filter(where)

    for key, value in filters.items():
        if key in POSSIBLE_DIRECT_FILTERS and value:
            if isinstance(value, str):
                where.append(f"{key} = %({key})s")
            elif isinstance(value, list):
                where.append(f"{key} IN %({key})s")
        if key in POSSIBLE_INDIRECT_FILTERS and value:
            eval(f"get_{key}_filter(where)")
        if key in COUNT_FILTERS:
            where.append(f"{key} != 0")
    if where:
        return " AND ".join(where)


def get_date_range_filter(where):
    where.append(
        "((" +
        "updated_at <= %(end_date)s AND updated_at >= %(start_date)s) OR " +
        "(created_at >= %(start_date)s AND created_at <= %(end_date)s))"
    )

def get_cargo_clearance_date_filter(where):
    where.append(
        "validity_end >= %(cargo_clearance_date)s AND validity_start <= %(cargo_clearance_date)s"
    )


def get_stale_rates_filter(where):
    where.append("checkout_count = 0 AND dislikes_count = 0 AND likes_count = 0")


def get_weight_slabs_filter(where):
    where.append("lower_limit >= %(lower_limit)s AND upper_limit <= %(upper_limit)s")

def get_chargeable_weight_filter(where):
    where.append("lower_limit <= %(chargeable_weight)s AND upper_limit >= %(chargeable_weight)s")

def get_rate_updated_at_less_than_filter(where):
    where.append("rate_updated_at < %(rate_updated_at_less_than)s")


def get_validity_end_greater_than_filter(where):
    where.append("validity_end > %(validity_end_greater_than)s")


def get_validity_end_less_than_filter(where):
    where.append("validity_end < %(validity_end_less_than)s")


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
        location_object["origin_airport"] = port_code_to_location_details_mapping.get(
            origin_port_code
        )

        filters["origin_airport_id"] = location_object["origin_airport"]["id"]

    if destination_port_code:
        location_object["destination_airport"] = port_code_to_location_details_mapping.get(
            destination_port_code
        )
        filters["destination_airport_id"] = location_object["destination_airport"]["id"]
