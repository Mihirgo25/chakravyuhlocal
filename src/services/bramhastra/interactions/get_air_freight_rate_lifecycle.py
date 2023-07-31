from services.bramhastra.helpers.clickhouse_helper import ClickHouse
from fastapi.encoders import jsonable_encoder
from services.bramhastra.helpers.air_freight_filter_helper import (
    get_direct_indirect_filters as get_direct_indirect_filters_for_rate,
)
from datetime import date, timedelta, datetime
import math

POSSIBLE_DIRECT_FILTERS = {
    "origin_port_id",
    "origin_country_id",
    "origin_trade_id",
    "origin_continent_id",
    "destination_port_id",
    "destination_country_id",
    "destination_trade_id",
    "destination_continent_id",
    "origin_region_id",
    "destination_region_id",
    "shipping_line_id",
    "importer_exporter_id",
    "container_size",
    "container_type",
    "commodity",
    "origin_main_port_id",
    "destination_main_port_id",
}

POSSIBLE_INDIRECT_FILTERS = {}

REQUIRED_FILTERS = {
    "start_date": datetime(2016, 5, 3).date(),
    "end_date": date.today() + timedelta(days=30),
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


async def get_air_freight_rate_lifecycle(filters):
    where = get_direct_indirect_filters_for_rate(filters)

    search_to_book_statistics = await get_search_to_book_and_feedback_statistics(
        filters.copy(), where
    )

    missing_rates_statistics = await get_missing_rates(filters.copy(), where)

    stale_rate_statistics = await get_stale_rate_statistics(filters.copy(), where)

    statistics = [
        [
            {
                "action_type": "checkout",
                "rates_count": search_to_book_statistics["checkout"],
                "drop": search_to_book_statistics["checkout_percentage"],
            },
            {
                "action_type": "booking_confirm",
                "rates_count": search_to_book_statistics[
                    "shipment_confirmed_by_service_provider"
                ],
                "drop": search_to_book_statistics["confirmed_booking_percentage"],
            },
            {
                "action_type": "revenue_desk",
                "rates_count": search_to_book_statistics["revenue_desk_visit"],
                "drop": search_to_book_statistics["revenue_desk_visit_percentage"],
            },
            {
                "action_type": "so1",
                "rates_count": search_to_book_statistics["so1_visit"],
                "drop": search_to_book_statistics["so1_visit_percentage"],
            },
        ],
        [
            {
                "action_type": "missing_rates",
                "rates_count": missing_rates_statistics["missing_rates"],
                "drop": missing_rates_statistics["missing_rates_percentage"],
            },
            {
                "action_type": "rates_triggered",
                "rates_count": missing_rates_statistics["rate_reverted"],
                "drop": 0
                if math.isnan(missing_rates_statistics["rate_reverted_percentage"])
                else missing_rates_statistics["rate_reverted_percentage"],
            },
        ],
        [
            {
                "action_type": "disliked_rates",
                "rates_count": search_to_book_statistics["dislikes"],
                "drop": search_to_book_statistics["dislikes_percentage"],
            },
            {
                "action_type": "feedback_received",
                "rates_count": search_to_book_statistics["feedback_recieved"],
                "drop": search_to_book_statistics["feedback_recieved_percentage"],
            },
            {
                "action_type": "rates_reverted",
                "rates_count": search_to_book_statistics["dislikes_rate_reverted"],
                "drop": search_to_book_statistics["dislikes_rate_reverted_percentage"],
            },
        ],
        [
            {
                "action_type": "stale_rates",
                "rates_count": stale_rate_statistics["stale_rates"],
            },
        ],
    ]

    return dict(searches=search_to_book_statistics["spot_search"], cards=statistics)


async def get_stale_rate_statistics(filters, where):
    clickhouse = ClickHouse()

    queries = [
        """SELECT count(id) as stale_rates FROM brahmastra.air_freight_rate_statistics WHERE checkout_count = 0 AND dislikes_count = 0 AND likes_count = 0"""
    ]

    if where:
        queries.append("AND")
        queries.append(where)

    if charts := jsonable_encoder(clickhouse.execute(" ".join(queries), filters)):
        return charts[0]


async def get_missing_rates(filters, rate_where):
    clickhouse = ClickHouse()

    where = get_direct_indirect_filters(filters)

    query1 = [
        """WITH spot_search AS (SELECT SUM(spot_search_count) AS count FROM brahmastra.air_freight_rate_statistics"""
    ]

    query2 = [
        """),missing_rates AS (SELECT count(id) AS count FROM brahmastra.air_freight_rate_request_statistics WHERE source = 'spot_search'"""
    ]
    query3 = [
        """),rate_reverted AS (SELECT count(id) AS count FROM brahmastra.air_freight_rate_request_statistics WHERE is_rate_reverted = true """
    ]

    query4 = """) SELECT missing_rates.count as missing_rates,(1-missing_rates/spot_search.count)*100 as missing_rates_percentage,rate_reverted.count as rate_reverted,(1 - rate_reverted.count/missing_rates)*100 as rate_reverted_percentage FROM missing_rates, rate_reverted, spot_search"""

    if where:
        query1.append(f"WHERE {rate_where}")
        query2.append(f"AND {where}")
        query3.append(f"AND {where}")

    if missing_rates := jsonable_encoder(
        clickhouse.execute(
            "".join([" ".join(query1), " ".join(query2), " ".join(query3), query4]),
            filters,
        )
    ):
        return missing_rates[0]


async def get_search_to_book_and_feedback_statistics(filters, where):
    clickhouse = ClickHouse()
    queries = [
        """SELECT SUM(spot_search_count) as spot_search,
        SUM(checkout_count) as checkout,
        FLOOR((1-SUM(checkout_count)/spot_search),2)*100 AS checkout_percentage,
        SUM(shipment_confirmed_by_service_provider_count) AS shipment_confirmed_by_service_provider,
        FLOOR((1-SUM(shipment_confirmed_by_service_provider_count)/checkout),2)*100 AS confirmed_booking_percentage,
        SUM(revenue_desk_visit_count) AS revenue_desk_visit,
        FLOOR((1-SUM(revenue_desk_visit_count)/SUM(shipment_confirmed_by_service_provider_count)),2)*100 AS revenue_desk_visit_percentage,
        SUM(so1_visit_count) AS so1_visit,
        FLOOR((1-SUM(so1_visit_count)/revenue_desk_visit),2)*100 AS so1_visit_percentage,
        SUM(dislikes_count) as dislikes,
        FLOOR((1-SUM(dislikes_count)/spot_search),2)*100 AS dislikes_percentage,
        SUM(feedback_recieved_count) AS feedback_recieved,
        FLOOR((1-SUM(feedback_recieved_count)/dislikes),2)*100 AS feedback_recieved_percentage,
        SUM(dislikes_rate_reverted_count) as dislikes_rate_reverted,
        FLOOR((1-SUM(dislikes_rate_reverted_count)/feedback_recieved),2)*100 AS dislikes_rate_reverted_percentage
        FROM brahmastra.air_freight_rate_statistics
        """
    ]

    if where:
        queries.append(" WHERE ")
        queries.append(where)

    if charts := jsonable_encoder(clickhouse.execute(" ".join(queries), filters)):
        return charts[0]
