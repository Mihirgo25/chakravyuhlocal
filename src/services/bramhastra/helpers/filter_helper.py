from datetime import date, timedelta, datetime

POSSIBLE_DIRECT_FILTERS = {
    "origin_port_id",
    "origin_country_id",
    "origin_trade_id",
    "origin_continent_id",
    "destination_port_id",
    "destination_country_id",
    "destination_trade_id",
    "destination_continent_id",
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
    "mode",
    "sourced_by_id",
    "procured_by_id",
    "origin_region_id",
    "destination_region_id"
}

POSSIBLE_INDIRECT_FILTERS = {}

REQUIRED_FILTERS = {
    "start_date": datetime(2016, 5, 3).date(),
    "end_date": date.today() + timedelta(days=30),
}

NEEDED_MODES = {"rate_extension", "cluster_extension", "predicted", "manual"}


def get_direct_indirect_filters(filters):
    for k, v in REQUIRED_FILTERS.items():
        if k not in filters:
            filters[k] = v
    where = []
    get_date_range_filter(where)

    for key in filters.keys():
        if key in POSSIBLE_DIRECT_FILTERS:
            where.append(f"{key} = %({key})s")
        if key in POSSIBLE_INDIRECT_FILTERS:
            eval(f"get_{key}_filter(where)")

    if where:
        return " AND ".join(where)


def get_date_range_filter(where):
    where.append(
        "((validity_end <= %(end_date)s AND validity_end >= %(start_date)s) OR (validity_start >= %(start_date)s AND validity_start <= %(end_date)s))"
    )