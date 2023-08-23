from services.bramhastra.client import ClickHouse
from fastapi.encoders import jsonable_encoder
from services.bramhastra.helpers.fcl_freight_filter_helper import add_pagination_data
from services.bramhastra.models.fcl_freight_rate_request_statistics import (
    FclFreightRateRequestStatistic,
)
from micro_services.client import maps

from datetime import date, timedelta, datetime


DEFAULT_INCUDE_PARAMS = {
    "origin_port_id",
    "destination_port_id",
    "container_size",
    "commodity",
    "is_rate_reverted",
    "source",
}

REQUIRED_FILTERS = {
    "start_date": datetime(2016, 5, 3).date(),
    "end_date": date.today() + timedelta(days=30),
}


POSSIBLE_DIRECT_FILTERS = {
    "origin_port_id",
    "destination_port_id",
    "container_size",
    "commodity",
    "is_rate_reverted",
    "source",
}

POSSIBLE_INDIRECT_FILTERS = {}

LOCATION_KEYS = {
    "origin_port_id",
    "destination_port_id",
    "origin_main_port_id",
    "destination_main_port_id",
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

    if where:
        return " AND ".join(where)


def get_date_range_filter(where):
    where.append(
        "((updated_at <= %(end_date)s AND updated_at >= %(start_date)s) OR (created_at >= %(start_date)s AND created_at <= %(end_date)s))"
    )


def add_service_objects(statistics):
    if not statistics:
        return
    location_ids = set()

    for statistic in statistics:
        for k, v in statistic.items():
            if k in LOCATION_KEYS:
                location_ids.add(v)

    locations = get_locations(location_ids)

    for statistic in statistics:
        update_statistic = dict()
        for k, v in statistic.items():
            if k in LOCATION_KEYS:
                location = locations.get(v)
                if not location:
                    continue
                update_statistic[f"{k[:-3]}"] = location
        statistic.update(update_statistic)


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


def list_fcl_freight_rate_request_statistics(filters={}, page_limit=10, page=1):
    clickhouse = ClickHouse()

    select = ",".join(DEFAULT_INCUDE_PARAMS)

    queries = [
        f"""SELECT {select} from brahmastra.{FclFreightRateRequestStatistic._meta.table_name}"""
    ]

    if where := get_direct_indirect_filters(filters):
        queries.append("WHERE")
        queries.append(where)

    total_count, total_pages = add_pagination_data(
        clickhouse, queries, filters, page, page_limit
    )

    statistics = jsonable_encoder(clickhouse.execute(" ".join(queries), filters))

    add_service_objects(statistics)

    return dict(
        list=statistics,
        page=page,
        page_limit=page_limit,
        total_pages=total_pages,
        total_count=total_count,
    )
