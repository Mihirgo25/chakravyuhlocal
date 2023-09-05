from datetime import date, timedelta, datetime
from math import ceil

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

POSSIBLE_INDIRECT_FILTERS = {"stale_rate","weight_slabs"}

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
            where.append(f"{key} = %({key})s")
        if key in POSSIBLE_INDIRECT_FILTERS and value:
            eval(f"get_{key}_filter(where)")
        if key in COUNT_FILTERS:
            where.append(f"{key} != 0")

    if where:
        return " AND ".join(where)


def get_date_range_filter(where):
    where.append(
        "((validity_end >= %(start_date)s AND validity_start <= %(start_date)s) OR (validity_start <= %(end_date)s AND validity_end >= %(end_date)s) OR (validity_end <= %(end_date)s AND validity_start >= %(start_date)s))"
    )


def get_stale_rates_filter(where):
    where.append("checkout_count = 0 AND dislikes_count = 0 AND likes_count = 0")
    

def get_weight_slabs_filter(where):
    where.append("lower_limit >= %(lower_limit)s AND upper_limit <= %(upper_limit)s")


def add_pagination_data(clickhouse, queries, filters, page, page_limit):
    total_count = clickhouse.execute(
        f"SELECT COUNT() as count FROM ({' '.join(queries)})", filters
    )[0]["count"]

    offset = (page - 1) * page_limit
    queries.append(f"LIMIT {page_limit} OFFSET {offset}")
    total_pages = ceil(total_count / page_limit)

    return total_count, total_pages
