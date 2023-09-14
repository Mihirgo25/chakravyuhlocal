from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from services.bramhastra.enums import FclDefault, Paginate
from services.bramhastra.client import ClickHouse
from micro_services.client import maps, common
from fastapi.encoders import jsonable_encoder
from services.bramhastra.enums import Fcl

DIRECT_FILTERS = {
    "commodity": FclDefault.commodity.value,
    "container_size": FclDefault.container_size.value,
    "container_type": FclDefault.container_type.value,
    "shipping_line_id": None,
}

FREQUENCY = {
    "year": "toStartOfMonth(toDate(updated_at))",
    "month": "toStartOfMonth(toDate(updated_at))",
    "week": "toStartOfWeek(toDate(updated_at))",
    "day": "toDate(updated_at)",
}

DEFAULT_AGGREGATE_SELECT = {
    "past_freight_rate": "AVG(bas_standard_price)",
    "current_freight_rate": "argMax(bas_standard_price, updated_at)",
}

LOCATION_KEYS = ["origin_port_id", "destination_port_id"]


def list_fcl_freight_recommended_trends(filters, limit, is_service_object_required):
    where = get_where(filters)

    trends = get_trends(where, filters, limit)

    change_currency(trends, filters)

    if is_service_object_required:
        add_service_objects(trends)

    return trends


def add_service_objects(trends):
    location_ids = set()
    for trend in trends:
        for k in LOCATION_KEYS:
            location_ids.add(trend.get(k))

    locations = maps.list_locations(
        {
            "filters": {"id": list(location_ids)},
            "includes": {
                "id": True,
                "name": True,
                "display_name": True,
                "port_code": True,
                "type": True,
                "flag_icon_url": True,
            },
            "page_limit": Paginate.global_limit.value,
        }
    ).get("list")

    if not locations:
        return

    location_id_to_details_mapping = {
        location["id"]: location for location in locations
    }

    for trend in trends:
        for k in LOCATION_KEYS:
            trend[k[:-3]] = location_id_to_details_mapping.get(trend.get(k))
            del trend[k]


def get_trends(where: str, filters: dict, limit: int) -> list:
    select = ",".join([k for k in DIRECT_FILTERS] + LOCATION_KEYS)

    aggregate_select = ",".join(
        [
            f"{v} AS {k}"
            for k, v in filters.get(
                "aggregate_select", DEFAULT_AGGREGATE_SELECT
            ).items()
        ]
    )

    query = [
        f"SELECT origin_port_id,destination_port_id,{aggregate_select}, SUM(spot_search_count) as searches, 'USD' as freight_rate_currency from brahmastra.{FclFreightRateStatistic._meta.table_name}"
    ]
    if where:
        query.append(f"WHERE {where} AND is_deleted = false")
    query.append(f"GROUP BY {select}")
    query.append(f"ORDER BY searches DESC LIMIT {limit}")

    return jsonable_encoder(ClickHouse().execute(" ".join(query), filters))


def get_where(filters: dict) -> str:
    where = []
    for k in DIRECT_FILTERS:
        if filters.get(k):
            if isinstance(filters.get(k), str):
                where.append(f"{k} = %({k})s")
            elif isinstance(filters.get(k), list):
                where.append(f"{k} in %({k})s")
    return " AND ".join(where) if where else None


def change_currency(trends, filters):
    exchange_rate = 1

    if (
        filters.get("currency")
        and filters.get("currency") != Fcl.default_currency.value
    ):
        exchange_rate = common.get_exchange_rate(
            {
                "from_currency": Fcl.default_currency.value,
                "to_currency": filters.get("currency"),
            }
        )

    for trend in trends:
        del trend["searches"]
        for key in DEFAULT_AGGREGATE_SELECT:
            if trend.get(key):
                trend[key] = trend[key] * exchange_rate
            trend["percentage_change"] = (
                (trend["current_freight_rate"] - trend["past_freight_rate"])
                / (trend["past_freight_rate"] or 1)
            ) * 100
        if filters.get("currency"):
            trend["freight_rate_currency"] = filters.get("currency")
