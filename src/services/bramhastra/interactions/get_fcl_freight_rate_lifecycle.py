from services.bramhastra.client import ClickHouse
from fastapi.encoders import jsonable_encoder
from datetime import date, timedelta, datetime
import math
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from services.bramhastra.models.fcl_freight_action import FclFreightAction
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic 
)
from services.bramhastra.interactions.list_fcl_freight_rate_request_statistics import (
    get_direct_indirect_filters as get_direct_indirect_filters_for_rate_request,
)
from services.bramhastra.config import LifeCycleConfig
import concurrent.futures
from services.bramhastra.enums import (
    ShipmentState, FeedbackType, FeedbackState, ShipmentServiceState, RateRequestState, RevenueDeskState
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
    "rate_type"
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
        searches=lifecycle_statistics["spot_search"],
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
    spot_search = [
        f"""
        SELECT COUNT(DISTINCT spot_search_id) AS spot_search FROM brahmastra.{FclFreightAction._meta.table_name}
        """
    ]
    checkout = [generate_sum_query("checkout")]
    shipment = [generate_sum_query("shipment")]

    confirmed = [avg_group_by_query(ShipmentState.confirmed_by_importer_exporter.name)]
    completed = [avg_group_by_query(ShipmentState.completed.name)]
    cancelled = [avg_group_by_query(ShipmentState.cancelled.name)]
    aborted = [avg_group_by_query(ShipmentState.aborted.name)]

    revenue_desk = [generate_revenue_select_query(RevenueDeskState.visited.name)]
    so1 = [generate_revenue_select_query(RevenueDeskState.selected_for_preference.name)]

    # Feedback
    feedbacks_created = [feedback_query(FeedbackState.created.name)]
    feedback_closed= [feedback_query(FeedbackState.closed.name)]
    feedback_rates_added = [feedback_query(FeedbackState.rate_added.name)]

    disliked = [count_boolean_query(FeedbackType.disliked.name)]
    liked = [count_boolean_query(FeedbackType.liked.name)]

    rate_reverted_feedbacks = [
        f"""
        SELECT COUNT(DISTINCT rate_id) AS rate_reverted_feedbacks FROM brahmastra.{FclFreightRateStatistic._meta.table_name} WHERE source = 'disliked_rate'
        """
    ]
    rates_requested = [rate_request_query(RateRequestState.created.name)]
    rates_reverted = [rate_request_query(RateRequestState.rate_added.name)]
    rates_closed = [rate_request_query(RateRequestState.closed.name)]


    variables = [
        spot_search,
        feedbacks_created,
        checkout,
        shipment,
        confirmed,
        completed,
        aborted,
        cancelled,
        revenue_desk,
        so1,
        disliked,
        feedback_closed,
        rate_reverted_feedbacks,
        feedback_rates_added,
        liked,
        rates_requested,
        rates_reverted,
        rates_closed,
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
        rates_requested.append(f"AND {missing_rates_where}")

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
        "spot_search": result["spot_search"],
        
        "checkout_count": result["checkout_count"],
        "checkout_dropoff": calculate_dropoff(
            result["checkout_count"], result["spot_search"]
        ),
        "shipment_count": result["shipment_count"],
        "shipment_dropoff": calculate_dropoff(
            result["shipment_count"], result["checkout_count"]
        ),
        "confirmed_count": result["shipment_confirmed_by_importer_exporter_count"],
        "confirmed_dropoff": calculate_dropoff(
            result["shipment_confirmed_by_importer_exporter_count"],
            result["shipment_count"],
        ),
        "completed_count": result["shipment_completed_count"],
        "completed_dropoff": calculate_dropoff(
            result["shipment_completed_count"], result["shipment_count"]
        ),
        "aborted_count": result["shipment_aborted_count"],
        "aborted_dropoff": calculate_dropoff(
            result["shipment_aborted_count"], result["shipment_count"]
        ),
        "cancelled_count": result["shipment_cancelled_count"],
        "cancelled_dropoff": calculate_dropoff(
            result["shipment_cancelled_count"], result["shipment_count"]
        ),
        "revenue_desk_count": result["revenue_visited_count"],
        "revenue_desk_dropoff": calculate_dropoff(
            result["revenue_visited_count"], result["shipment_count"]
        ),
        "so1_count": result["revenue_selected_for_preference_count"],
        "so1_dropoff": calculate_dropoff(
            result["revenue_selected_for_preference_count"], result["revenue_visited_count"]
        ),
        # Feedback
        "feedbacks_created_count": result["feedbacks_created"],
        "feedbacks_created_dropoff": calculate_dropoff(
            result["feedbacks_created"], result["spot_search"]
        ),
        "disliked_count": result["disliked_count"],
        "disliked_dropoff": calculate_dropoff(
            result["disliked_count"], result["feedbacks_created"]
        ),
        "liked_count": result["liked_count"],
        "liked_dropoff": calculate_dropoff(
            result["liked_count"], result["spot_search"]
        ),
        "feedback_closed_count": result["feedbacks_closed"],
        "feedback_closed_dropoff": calculate_dropoff(
            result["feedbacks_closed"], result["disliked_count"]
        ),
        "rate_reverted_feedbacks_count": result["rate_reverted_feedbacks"],
        "rate_reverted_feedbacks_dropoff": calculate_dropoff(
            result["rate_reverted_feedbacks"], result["feedbacks_closed"]
        ),
        "feedback_rates_added_count": result["feedbacks_rate_added"],

        # rate requests
        "rates_requested_count": result["rate_request_created_count"],
        "rates_requested_dropoff": calculate_dropoff(
            result["rate_request_created_count"], result["spot_search"]
        ),
        "requests_closed_count": result["rate_request_closed_count"],
        "requests_closed_dropoff": calculate_dropoff(
            result["rate_request_closed_count"], result["rate_request_created_count"]
        ),
        "rates_reverted_count": result["rate_request_rate_added_count"],
        "rates_reverted_dropoff": calculate_dropoff(
            result["rate_request_rate_added_count"], result["rate_request_closed_count"]
        ),
    }
    return lifecycle_statistics


def filter_out_of_range_value(val):
    if math.isinf(val) or math.isnan(val):
        return 0
    return val


def generate_sum_query(column):
    return f"""
        SELECT COUNT(DISTINCT {column}_id) AS {column}_count FROM brahmastra.{FclFreightAction._meta.table_name} WHERE {column} > 0
        """

def generate_revenue_select_query(column):
    return f"""
        SELECT COUNT(*) AS revenue_{column}_count FROM brahmastra.{FclFreightAction._meta.table_name} WHERE revenue_desk_state = '{column}'
        """

def count_boolean_query(column):
    return f"""
    SELECT COUNT(*) AS {column}_count FROM brahmastra.{FclFreightAction._meta.table_name} WHERE feedback_type = '{column}'
    """


def avg_group_by_query(column):
    return f"""
    SELECT COUNT(DISTINCT shipment_id) AS shipment_{column}_count FROM brahmastra.{FclFreightAction._meta.table_name} WHERE shipment_state = '{column}'
    """

def rate_request_query(column):
    return f"""
    SELECT COUNT(*) AS rate_request_{column}_count FROM brahmastra.{FclFreightAction._meta.table_name} WHERE rate_request_state = '{column}'
    """

def feedback_query(column):
    return f"""
    SELECT COUNT(DISTINCT rate_id) AS feedbacks_{column} FROM brahmastra.{FclFreightAction._meta.table_name} WHERE feedback_state = '{column}'
    """

def calculate_dropoff(numerator, denominator):
    if denominator == 0:
        denominator = 1
    return round((1 - (numerator / denominator)) * 100,2)