from services.bramhastra.client import ClickHouse
from fastapi.encoders import jsonable_encoder
from datetime import date, timedelta, datetime
import math
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from services.bramhastra.models.fcl_freight_action import FclFreightAction
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from services.bramhastra.interactions.list_fcl_freight_rate_request_statistics import (
    get_direct_indirect_filters as get_direct_indirect_filters_for_rate_request,
)
from services.bramhastra.config import LifeCycleConfig
import concurrent.futures
from services.bramhastra.enums import (
    ShipmentState,
    FeedbackType,
    FeedbackState,
    ShipmentServiceState,
    RateRequestState,
    RevenueDeskState,
)

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
    "parent_mode",
    "parent_rate_mode",
    "rate_type",
}

POSSIBLE_INDIRECT_FILTERS = {}

REQUIRED_FILTERS = {
    "start_date": datetime(2016, 5, 3).date(),
    "end_date": date.today() + timedelta(days=30),
}


def get_direct_indirect_filters(filters, where):
    for k, v in REQUIRED_FILTERS.items():
        if k not in filters:
            filters[k] = v
    get_date_range_filter(where, filters)

    for key, value in filters.items():
        if key in POSSIBLE_DIRECT_FILTERS and value:
            if isinstance(value, str):
                where.append(f"{key} = %({key})s")
            elif isinstance(value, list):
                where.append(f"{key} IN %({key})s")
        if key in POSSIBLE_INDIRECT_FILTERS and value:
            eval(f"get_{key}_filter(where)")

    if where:
        return " AND ".join(where)


def get_date_range_filter(where, filters):
    where.append(
        f" ((updated_at >= ('{filters['start_date']}') AND updated_at <= ('{filters['end_date']}')) OR (created_at >= ('{filters['start_date']}') AND created_at <= ('{filters['end_date']}')))"
    )


async def get_fcl_freight_rate_lifecycle(filters):
    where = []
    get_direct_indirect_filters(filters, where)

    lifecycle_statistics = await get_lifecycle_statistics(filters, where)

    graph = LifeCycleConfig(lifecycle_statistics).fill_flows()

    return dict(
        searches=lifecycle_statistics["spot_search_count"],
        graph=graph,
    )


async def get_stale_rate_statistics(filters, where):
    clickhouse = ClickHouse()

    queries = [
        f"""SELECT count(DISTINCT rate_id) as idle_rates FROM brahmastra.{FclFreightRateStatistic._meta.table_name} WHERE checkout_count = 0 AND dislikes_count = 0 AND likes_count = 0"""
    ]

    if where:
        queries.append("AND")
        queries.append(where)

    if charts := jsonable_encoder(clickhouse.execute(" ".join(queries), filters)):
        return charts[0]


async def get_lifecycle_statistics(filters, where):
    # Business
    spot_search_count = [distict_id_query("spot_search")]

    checkout_count = [non_zero_distinct_id_query("checkout")]

    shipments_received = [shipment_query(ShipmentState.shipment_received.name, "=")]
    shipments_confirmed_by_importer_exporter = [
        shipment_query(ShipmentState.confirmed_by_importer_exporter.name, "=")
    ]
    shipments_completed = [shipment_query(ShipmentState.completed.name, "=")]
    shipments_cancelled = [shipment_query(ShipmentState.cancelled.name, "=")]
    shipments_aborted = [shipment_query(ShipmentState.aborted.name, "=")]

    revenue_desk_visited = [revenue_desk_query(RevenueDeskState.visited.name, "=")]
    revenue_desk_selected_for_booking = [
        revenue_desk_query(RevenueDeskState.selected_for_booking.name, "=")
    ]

    # Feedback
    feedbacks_created = [feedback_query(FeedbackState.created.name, "=")]
    feedbacks_closed = [feedback_query(FeedbackState.closed.name, "=")]
    feedbacks_rate_added = [feedback_query(FeedbackState.rate_added.name, "=")]

    disliked = [count_boolean_query(FeedbackType.disliked.name)]
    liked = [count_boolean_query(FeedbackType.liked.name)]

    rates_source_disliked = [
        f"""
        SELECT COUNT(DISTINCT rate_id) AS rates_source_disliked FROM brahmastra.{FclFreightRateStatistic._meta.table_name} WHERE source = 'disliked_rate'
        """
    ]
    rate_requests_created = [rate_request_query(RateRequestState.created.name, "=")]
    rate_requests_closed = [rate_request_query(RateRequestState.closed.name, "=")]
    rate_requests_rate_added = [
        rate_request_query(RateRequestState.rate_added.name, "=")
    ]

    variables = [
        spot_search_count,
        feedbacks_created,
        checkout_count,
        shipments_received,
        shipments_confirmed_by_importer_exporter,
        shipments_completed,
        shipments_cancelled,
        shipments_aborted,
        revenue_desk_visited,
        revenue_desk_selected_for_booking,
        disliked,
        feedbacks_closed,
        rates_source_disliked,
        feedbacks_rate_added,
        liked,
        rate_requests_created,
        rate_requests_closed,
        rate_requests_rate_added,
    ]
    if where:
        query = " AND ".join(where)
        for var in variables:
            if "where" in " ".join(var).lower():
                var.append(f" AND {query} ")
            else:
                var.append(f" WHERE {query} ")

    missing_rates_filter = filters.copy()

    missing_rates_where = get_direct_indirect_filters_for_rate_request(
        missing_rates_filter
    )

    if missing_rates_where:
        rate_requests_created.append(f"AND {missing_rates_where}")

    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for var in variables:
            futures.append(
                executor.submit(ClickHouse().execute, " ".join(var), filters)
            )

    for i in range(0, len(futures)):
        results.append(futures[i].result()[0])
    result = {}
    for count in results:
        result.update(count)

    lifecycle_statistics = {
        # buisness flow
        "spot_search_count": result["spot_search_count"],
        "checkout_count": result["checkout_count"],
        "checkout_dropoff": calculate_dropoff(
            result["checkout_count"], result["spot_search_count"]
        ),
        "shipments_received": result["shipments_shipment_received"],
        "shipment_dropoff": calculate_dropoff(
            result["shipments_shipment_received"], result["checkout_count"]
        ),
        "confirmed_count": result["shipments_confirmed_by_importer_exporter"],
        "confirmed_dropoff": calculate_dropoff(
            result["shipments_confirmed_by_importer_exporter"],
            result["shipments_shipment_received"],
        ),
        "completed_count": result["shipments_completed"],
        "completed_dropoff": calculate_dropoff(
            result["shipments_completed"],
            result["shipments_confirmed_by_importer_exporter"],
        ),
        "aborted_count": result["shipments_aborted"],
        "aborted_dropoff": calculate_dropoff(
            result["shipments_aborted"],
            result["shipments_confirmed_by_importer_exporter"],
        ),
        "cancelled_count": result["shipments_cancelled"],
        "cancelled_dropoff": calculate_dropoff(
            result["shipments_cancelled"],
            result["shipments_confirmed_by_importer_exporter"],
        ),
        "revenue_desk_count": result["revenue_desk_visited"],
        "revenue_desk_dropoff": calculate_dropoff(
            result["revenue_desk_visited"],
            result["shipments_confirmed_by_importer_exporter"],
        ),
        "so1_count": result["revenue_desk_selected_for_booking"],
        "so1_dropoff": calculate_dropoff(
            result["revenue_desk_selected_for_booking"],
            result["revenue_desk_visited"],
        ),
        # Feedback
        "feedbacks_created_count": result["feedbacks_created"],
        "feedbacks_created_dropoff": calculate_dropoff(
            result["feedbacks_created"], result["spot_search_count"]
        ),
        "disliked_count": result["disliked_count"],
        "disliked_dropoff": calculate_dropoff(
            result["disliked_count"], result["feedbacks_created"]
        ),
        "liked_count": result["liked_count"],
        "liked_dropoff": calculate_dropoff(
            result["liked_count"], result["spot_search_count"]
        ),
        "feedback_closed_count": result["feedbacks_closed"],
        "feedback_closed_dropoff": calculate_dropoff(
            result["feedbacks_closed"], result["disliked_count"]
        ),
        "rates_source_disliked_count": result["rates_source_disliked"],
        "feedbacks_with_rate_added": result["feedbacks_rate_added"],
        "feedbacks_with_rate_added_dropoff": calculate_dropoff(
            result["feedbacks_rate_added"], result["feedbacks_closed"]
        ),
        # rate requests
        "rates_requested_count": result["rate_requests_created"],
        "rates_requested_dropoff": calculate_dropoff(
            result["rate_requests_created"], result["spot_search_count"]
        ),
        "requests_closed_count": result["rate_requests_closed"],
        "requests_closed_dropoff": calculate_dropoff(
            result["rate_requests_closed"], result["rate_requests_created"]
        ),
        "rates_reverted_count": result["rate_requests_rate_added"],
        "rates_reverted_dropoff": calculate_dropoff(
            result["rate_requests_rate_added"], result["rate_requests_closed"]
        ),
    }
    return lifecycle_statistics


def filter_out_of_range_value(val):
    if math.isinf(val) or math.isnan(val):
        return 0
    return val


def distict_id_query(column):
    return f"""
        SELECT COUNT(DISTINCT {column}_id) AS {column}_count FROM brahmastra.{FclFreightAction._meta.table_name}
        """


def non_zero_distinct_id_query(column):
    return f"""
        {distict_id_query(column)} WHERE {column} > 0
        """


def revenue_desk_query(column, comparator):
    return f"""
        SELECT COUNT(DISTINCT shipment_id) AS revenue_desk_{column} FROM brahmastra.{FclFreightAction._meta.table_name} WHERE revenue_desk_state {comparator} '{column}'
        """


def count_boolean_query(column):
    return f"""
    SELECT COUNT(DISTINCT id) AS {column}_count FROM brahmastra.{FclFreightAction._meta.table_name} WHERE feedback_type = '{column}'
    """


def shipment_query(column, comparator):
    return f"""
    SELECT COUNT(DISTINCT shipment_id) AS shipments_{column} FROM brahmastra.{FclFreightAction._meta.table_name} WHERE shipment_state {comparator} '{column}'
    """


def rate_request_query(column, comparator):
    return f"""
    SELECT COUNT(DISTINCT id) AS rate_requests_{column} FROM brahmastra.{FclFreightAction._meta.table_name} WHERE rate_request_state {comparator} '{column}'
    """


def feedback_query(column, comparator):
    return f"""
    SELECT COUNT(DISTINCT rate_id) AS feedbacks_{column} FROM brahmastra.{FclFreightAction._meta.table_name} WHERE feedback_state {comparator} '{column}'
    """


def calculate_dropoff(numerator, denominator):
    if (numerator - denominator) != 0:
        return round((1 - (numerator / (denominator or 1))) * 100, 2)
    return 0
