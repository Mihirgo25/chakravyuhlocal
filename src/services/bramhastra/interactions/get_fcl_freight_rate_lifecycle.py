from services.bramhastra.client import ClickHouse
from fastapi.encoders import jsonable_encoder
from services.bramhastra.helpers.fcl_freight_filter_helper import (
    get_direct_indirect_filters as get_direct_indirect_filters_for_rate,
)
from datetime import date, timedelta, datetime
import math
from services.bramhastra.enums import FclModes
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic
)
from services.bramhastra.models.fcl_freight_action import FclFreightAction
from services.fcl_freight_rate.models.fcl_freight_rate_request import FclFreightRateRequest
from services.bramhastra.models.fcl_freight_rate_request_statistics import (
    FclFreightRateRequestStatistic,
)
from services.bramhastra.interactions.list_fcl_freight_rate_request_statistics import (
    get_direct_indirect_filters as get_direct_indirect_filters_for_rate_request,
)
from services.bramhastra.config import LifeCycleConfig
import concurrent.futures
from services.bramhastra.config import LifeCycleConfig 

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
            if isinstance(value, str):
                where.append(f"{key} = %({key})s")
            elif isinstance(value, list):
                where.append(f"{key} IN %({key})s")
        if key in POSSIBLE_INDIRECT_FILTERS and value:
            eval(f"get_{key}_filter(where)")

    if where:
        return " AND ".join(where)


def get_date_range_filter(where):
    where.append(
        "((updated_at <= %(end_date)s AND updated_at >= %(start_date)s) OR (created_at >= %(start_date)s AND created_at <= %(end_date)s))"
    )


async def get_fcl_freight_rate_lifecycle(filters):
    where = get_direct_indirect_filters_for_rate(filters)

    mode_wise_rate_count = await get_mode_wise_rate_count(filters.copy(), where)

    lifecycle_statistics = await get_lifecycle_statistics(filters.copy(), where)
    
    graph = LifeCycleConfig(lifecycle_statistics)
    graph_data = graph.fill_flows()

    return dict(
        mode_wise_rate_count=mode_wise_rate_count,
        searches=lifecycle_statistics["spot_search"],
        cards=lifecycle_statistics,
        graph=graph_data,
    )


async def get_stale_rate_statistics(filters, where):
    clickhouse = ClickHouse()

    queries = [f"""SELECT count(DISTINCT rate_id) as idle_rates FROM brahmastra.{FclFreightRateStatistic._meta.table_name} WHERE checkout_count = 0 AND dislikes_count = 0 AND likes_count = 0"""]

    if where:
        queries.append("AND")
        queries.append(where)

    if charts := jsonable_encoder(clickhouse.execute(" ".join(queries), filters)):
        return charts[0]


async def get_lifecycle_statistics(filters, where):
    #Buisness block 

    #rates shown

    rates_shown = [
        f"""
        SELECT COUNT(DISTINCT rate_id) AS count FROM brahmastra.{FclFreightAction._meta.table_name} WHERE spot_search > 0
        """ 
    ]
    liked = [count_boolean_query('liked')]
    disliked = [count_boolean_query('disliked')]
    feedback_closed = [
        f"""
        SELECT COUNT(*) AS count FROM brahmastra.{FclFreightAction._meta.table_name} WHERE status = 'inactive'
        """
    ]
    rate_reverted_feedbacks = [
        f"""
        SELECT SUM(is_reverted) AS count FROM brahmastra.{FclFreightRateRequestStatistic._meta.table_name} WHERE is_reverted = 1 GROUP BY rate_id
        """
    ]
    #?
    feedback_received_count = [
        f"""
        SELECT SUM(is_reverted) AS count FROM brahmastra.{FclFreightRateRequestStatistic._meta.table_name} WHERE disliked = 1 GROUP BY rate_id
        """
    ]
    #Feedback
    feedback_received_shipments = [generate_disliked_count_query('received')]
# - feedback
    ##missing 

    # source missing rates
    requests_closed = [
        f"""
        SELECT COUNT(*) AS count FROM brahmastra.{FclFreightRateRequest._meta.table_name} WHERE source = 'missing_rates' AND status = 'inactive'
        """
    ]  
    rates_requested= [
        f"""
        SELECT COUNT(DISTINCT rate_id) AS count FROM brahmastra.{FclFreightRateRequest._meta.table_name} WHERE source = 'missing_rates'
        """
    ]
    rates_reverted = [
        f"""
        SELECT SUM(is_reverted) AS count FROM brahmastra.{FclFreightRateRequestStatistic._meta.table_name} WHERE is_reverted = 1 GROUP BY rate_id
        """
    ]


    #Buisness branch 
    spot_search = [
        f"""
        SELECT COUNT(DISTINCT spot_search_id) AS count FROM brahmastra.{FclFreightAction._meta.table_name}
        """
    ]
    checkout = [generate_sum_query("checkout")]
    shipment = [generate_sum_query("shipment")]
    confirmed = [generate_count_query('confirmed_by_importer_exporter')]
    completed = [generate_count_query('completed')]
    aborted = [generate_count_query('aborted')]
    cancelled = [generate_count_query('cancelled')]
    revenue_desk = [generate_sum_query("revenue_desk_shown_rates")]
    so1 = [generate_sum_query("so1_select")]
    
    
    
    received_shipments = [generate_count_query('received')]
    


    variables = [
    spot_search, 
    rates_shown,
    checkout, 
    shipment, 
    so1,
    revenue_desk, 
    cancelled, 
    aborted, 
    received_shipments,
    confirmed, 
    completed,
    liked, 
    disliked, 
    feedback_closed, 
    
    rates_requested,
    rates_reverted, 

    feedback_received_shipments, 
    rate_reverted_feedbacks
    ]

    if where:
        for var in variables:
            var.append(f"AND {where}")
        
    missing_rates_filter = filters.copy()

    missing_rates_where = get_direct_indirect_filters_for_rate_request(
        missing_rates_filter
    )

    if missing_rates_where:
        rates_requested.append(f"AND {missing_rates_where}")

    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures =[]
        for var in variables:
            futures.append(executor.submit(ClickHouse().execute, " ".join(var), filters))

    for i in range(0, len(futures)):
            results.append(futures[i].result()[0])
    
    variables = results

    lifecycle_statistics = {
        #feedback-2
        "rates_shown_count": rates_shown["count"],
        "rates_shown_dropoff": (1 - (rates_shown["count"] / (spot_search["count"] or 1)))
        * 100,
        
        "disliked_count": disliked["count"],
        "disliked_dropoff": (1 - (disliked["count"] / (spot_search["count"] or 1)))
        * 100,

        "liked_count": liked["count"],
        "liked_dropoff": (1 - (liked["count"] / (spot_search["count"] or 1)))
        * 100,

        "rate_reverted_feedbacks_count": rate_reverted_feedbacks["count"],
        "rate_reverted_feedbacks_dropoff": (1 - (rate_reverted_feedbacks["count"] / (spot_search["count"] or 1)))* 100,

        "feedback_received_count": feedback_received_count["count"],
        "feedback_received_dropoff": (1 - (feedback_received_count["count"] / (spot_search["count"] or 1)))* 100,
        
        "feedback_rates_added_count": feedback_received_count["count"],
        "feedback_rates_added_dropoff": (1 - (feedback_received_count["count"] / (spot_search["count"] or 1)))* 100,

        #Checkout branch buisness-1
        "spot_search": spot_search["count"],
        "spot_search_dropoff": (1 - (spot_search["count"] / (rates_shown["count"] or 1)))* 100,

        "checkout_count": checkout["count"],
        "checkout_dropoff": (1 - (checkout["count"] / (spot_search["count"] or 1)))* 100,

        "shipment_count": shipment["count"],
        "shipment_dropoff": (1 - (shipment["count"] / (checkout["count"] or 1)))* 100,
        
        "confirmed_count": confirmed["count"],
        "confirmed_dropoff": (1 - (confirmed["count"] / shipment["count"] or 1))
        * 100,

        "completed_count": completed["count"],
        "completed_dropoff": (1 - (completed["count"] / shipment["count"] or 1))
        * 100,

        "aborted_count": aborted["count"],
        "aborted_dropoff": (1 - (aborted["count"] / shipment["count"] or 1))
        * 100,

        "cancelled_count": cancelled["count"],
        "cancelled_dropoff": (1 - (cancelled["count"] / shipment["count"] or 1))
        * 100,

        "revenue_desk_count": revenue_desk["count"],
        "revenue_desk_dropoff": (1 - (revenue_desk["count"] / (shipment["count"] or 1)))* 100,
        
        "so1_count": so1["count"],
        "so1_dropoff": (
            1 - (so1["count"] / (revenue_desk["count"] or 1)))* 100,

        #Missing- 3
        "rates_requested_count": rates_requested["count"],
        "rates_requested_dropoff": (
            1 - (rates_requested["count"] / (spot_search["count"] or 1))
        )
        * 100,
        "requests_closed_count": requests_closed["count"],
        "requests_closed_dropoff": (1 - (requests_closed["count"] / rates_shown["count"] or 1))
        * 100,
        "rates_reverted_count": rates_reverted["count"],
        "rates_reverted_dropoff": (1 - (rates_reverted["count"] / rates_shown["count"] or 1))
        * 100,


    }
    return lifecycle_statistics


async def get_mode_wise_rate_count(filters, where):
    clickhouse = ClickHouse()

    queries = [
        """SELECT parent_mode,COUNT(DISTINCT rate_id) as rate_count from brahmastra.fcl_freight_actions"""
    ]

    if where:
        queries.append(f" WHERE {where} AND is_deleted = false")

    queries.append("GROUP BY parent_mode")

    if charts := jsonable_encoder(clickhouse.execute(" ".join(queries), filters)):
        return charts


def filter_out_of_range_value(val):
    if math.isinf(val) or math.isnan(val):
        return 0
    return val
def generate_sum_query(column):
        return f"""
        SELECT SUM(sign*{column}) AS count FROM brahmastra.{FclFreightAction._meta.table_name} WHERE {column} > 0
        """
def generate_count_query(status):
    return f"""
    SELECT COUNT(DISTINCT shipment_id) AS count FROM brahmastra.{FclFreightAction._meta.table_name} WHERE shipment_status = '{status}'
    """
def generate_missing_rate_query(status):
    return f"""
    SELECT COUNT(DISTINCT shipment_id) AS count FROM brahmastra.{FclFreightAction._meta.table_name} WHERE shipment_status = '{status}' AND source = 'missing_rates'
    """ 
def generate_disliked_count_query(status):
    return f"""
    SELECT COUNT(DISTINCT shipment_id) AS count FROM brahmastra.{FclFreightAction._meta.table_name} WHERE shipment_status = '{status}' AND disliked = 1
    """ 
def count_boolean_query(column):
        return f"""
        SELECT SUM({column}) AS count FROM brahmastra.{FclFreightAction._meta.table_name} WHERE {column} = 1
        """
