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
import concurrent.futures

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

    def generate_statistic(action_type, percentage_key):
        return {
            "action_type": action_type,
            "rates_count": lifecycle_statistics[action_type],
            "drop": filter_out_of_range_value(lifecycle_statistics[percentage_key]),
        }
    
    statistics = [
        [
            generate_statistic("spot_search", "spot_search_percentage"),
        ],
        [
            generate_statistic("checkout","checkout_percentage"),
            
            generate_statistic("shipments","shipments_percentage"),
            
            generate_statistic("revenue_desk_shown_rates", "revenue_desk_shown_rates_percentage"),
            generate_statistic("revenue_desk_selected_rates", "revenue_desk_selected_rates_percentage"),
            
            generate_statistic("so1_select", "so1_select_percentage"),
            
            generate_statistic("cancelled_shipments", "cancelled_shipments_percentage"),
            generate_statistic("aborted_shipments", "aborted_shipments_percentage"),
            generate_statistic("received_shipments", "received_shipments_percentage"),
            generate_statistic("confirmed_by_importer_exporter_shipments", "confirmed_by_importer_exporter_shipments_percentage"),
            generate_statistic("completed_shipments","completed_shipments_percentage"),
        ],
        [
            generate_statistic("missing_rates","missing_rates_percentage"),
            generate_statistic("missing_closed", "missing_closed_percentage"),
            generate_statistic("missing_reverted", "missing_reverted_percentage" ),
            generate_statistic("missing_spot_search", "missing_spot_search_percentage"),
            generate_statistic("missing_checkout", "missing_checkout_percentage"),

            generate_statistic("missing_shipments", "missing_shipments_percentage"),
            
            generate_statistic("missing_cancelled_shipments", "missing_cancelled_shipments_percentage"),
            generate_statistic("missing_aborted_shipments", "missing_aborted_shipments_percentage"),
            generate_statistic("missing_received_shipments", "missing_received_shipments_percentage"),
            generate_statistic("missing_confirmed_by_importer_exporter_shipments", "missing_confirmed_by_importer_exporter_shipments_percentage"),
            generate_statistic("missing_completed_shipments","missing_completed_shipments_percentage"),
        ],
        [
            generate_statistic("dislike", "dislikes_percentage"),
            generate_statistic("like", "likes_percentage"),
            
            generate_statistic("feedback_closed", "feedback_closed_percentage"),
            generate_statistic("reverted", "reverted_percentage"),
            
            generate_statistic("feedback_spot_search","feedback_spot_search_percentage"),
            generate_statistic("feedback_checkout", "feedback_checkout_percentage"),
            
            generate_statistic("feedback_shipments","feedback_shipments_percentage"),
            
            generate_statistic("feedback_cancelled_shipments", "feedback_cancelled_shipments_percentage"),
            generate_statistic("feedback_aborted_shipments","feedback_aborted_shipments_percentage"),
            generate_statistic("feedback_received_shipments", "feedback_received_shipments_percentage"),
            generate_statistic("feedback_confirmed_by_importer_exporter_shipments", "feedback_confirmed_by_importer_exporter_shipments_percentage"),
            generate_statistic("feedback_completed_shipments", "feedback_completed_shipments_percentage"),            
        ],
    ]
    return dict(
        mode_wise_rate_count=mode_wise_rate_count,
        searches=lifecycle_statistics["spot_search"],
        cards=statistics,
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
    #Main block 
    spot_search = [
        f"""
        SELECT COUNT(DISTINCT spot_search_id) AS count FROM brahmastra.{FclFreightAction._meta.table_name} WHERE spot_search = 1
        """
    ]
    #rates shown

    rates_shown = [
        f"""
        SELECT SUM(spot_search) AS count FROM brahmastra.{FclFreightAction._meta.table_name} WHERE spot_search > 0
        """ 
    ]
    likes = [count_boolean_query('liked')]
    dislikes = [count_boolean_query('disliked')]
    feedback_closed = [
        f"""
        SELECT COUNT(*) AS count FROM brahmastra.{FclFreightAction._meta.table_name} WHERE status = 'inactive'
        """
    ]
    reverted = [
        f"""
        SELECT SUM(is_reverted) AS count FROM brahmastra.{FclFreightRateRequestStatistic._meta.table_name} WHERE is_reverted = 1 GROUP BY rate_id
        """
    ]
    total_rates = [
        f"""
        SELECT SUM(is_reverted) AS count FROM brahmastra.{FclFreightRateRequestStatistic._meta.table_name} WHERE disliked = 1 GROUP BY rate_id
        """
    ]
    #Feedback
    feedback_spot_search = [
        f"""
        SELECT COUNT(DISTINCT shipment_id) AS count FROM brahmastra.{FclFreightAction._meta.table_name} WHERE spot_search > 0 AND disliked = 1
        """ 
    ]
    feedback_checkout = [generate_disliked_count_query('checkout')]
    feedback_shipments = [generate_disliked_count_query('shipments')]
    feedback_cancelled_shipments = [generate_disliked_count_query('cancelled')]
    feedback_aborted_shipments = [generate_disliked_count_query('aborted')]
    feedback_received_shipments = [generate_disliked_count_query('received')]
    feedback_confirmed_by_importer_exporter_shipments = [generate_disliked_count_query('confirmed_by_importer_exporter')]
    feedback_completed_shipments = [generate_disliked_count_query('completed')]
    # - feedback
    ##missing 

    # source missing rates
    closed_requests = [
        f"""
        SELECT COUNT(*) AS count FROM brahmastra.{FclFreightRateRequest._meta.table_name} WHERE source = 'missing_rates' AND status = 'inactive'
        """
    ]  
    missing_rates= [
        f"""
        SELECT COUNT(DISTINCT rate_id) AS count FROM brahmastra.{FclFreightRateRequest._meta.table_name} WHERE source = 'missing_rates'
        """
    ]
    missing_reverted = [
        f"""
        SELECT SUM(is_reverted) AS count FROM brahmastra.{FclFreightRateRequestStatistic._meta.table_name} WHERE is_reverted = 1 GROUP BY rate_id
        """
    ]
    missing_spot_search = [
        f"""
        SELECT COUNT(DISTINCT shipment_id) AS count FROM brahmastra.{FclFreightAction._meta.table_name} WHERE spot_search > 0 AND source = 'missing_rates'
        """ 
    ]
    missing_checkout = [generate_missing_rate_query('checkout')]
    missing_shipments = [generate_missing_rate_query('shipments')]
    missing_cancelled_shipments = [generate_missing_rate_query('cancelled')]
    missing_aborted_shipments = [generate_missing_rate_query('aborted')]
    missing_received_shipments = [generate_missing_rate_query('received')]
    missing_confirmed_by_importer_exporter_shipments = [generate_missing_rate_query('confirmed_by_importer_exporter')]
    missing_completed_shipments = [generate_missing_rate_query('completed')]

    #Checkout branch 
    checkout = [generate_sum_query("checkout")]
    shipments = [generate_sum_query("shipment")]
    so1_select = [generate_sum_query("so1_select")]
    revenue_desk_shown_rates = [generate_sum_query("revenue_desk_shown_rates")]
    revenue_desk_selected_rates = [
        f"""
        SELECT COUNT(DISTINCT rate_id) AS count FROM brahmastra.{FclFreightAction._meta.table_name} WHERE revenue_desk_select > 0
        """
    ]
    cancelled_shipments = [generate_count_query('cancelled')]
    aborted_shipments = [generate_count_query('aborted')]
    received_shipments = [generate_count_query('received')]
    confirmed_by_importer_exporter_shipments = [generate_count_query('confirmed_by_importer_exporter')]
    completed_shipments = [generate_count_query('completed')]

    variables = [
    spot_search, 
    rates_shown,
    checkout, 
    shipments, 
    so1_select,
    revenue_desk_shown_rates, 
    revenue_desk_selected_rates,
    cancelled_shipments, 
    aborted_shipments, 
    received_shipments,
    confirmed_by_importer_exporter_shipments, 
    completed_shipments,
    likes, 
    dislikes, 
    feedback_closed, 
    reverted,
    missing_rates,
    missing_reverted, 
    missing_spot_search, 
    missing_checkout,
    missing_shipments,
    missing_cancelled_shipments, 
    missing_aborted_shipments, 
    missing_received_shipments,
    missing_confirmed_by_importer_exporter_shipments, 
    missing_completed_shipments,
    feedback_spot_search, 
    feedback_checkout,
    feedback_shipments,
    feedback_cancelled_shipments, 
    feedback_aborted_shipments, 
    feedback_received_shipments,
    feedback_confirmed_by_importer_exporter_shipments, 
    feedback_completed_shipments
    ]

    if where:
        for var in variables:
            var.append(f"AND {where}")
        
    missing_rates_filter = filters.copy()

    missing_rates_where = get_direct_indirect_filters_for_rate_request(
        missing_rates_filter
    )

    if missing_rates_where:
        missing_rates.append(f"AND {missing_rates_where}")

    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures =[]
        for var in variables:
            futures.append(executor.submit(ClickHouse().execute, " ".join(var), filters))

    for i in range(0, len(futures)):
            results.append(futures[i].result()[0])
    
    variables = results

    lifecycle_statistics = {
        #feedback
        "rates_shown": rates_shown["count"],

        "likes": dislikes["count"],
        "likes_percentage": (1 - (likes["count"] / (spot_search["count"] or 1)))
        * 100,
        "dislikes": dislikes["count"],
        "dislikes_percentage": (1 - (dislikes["count"] / (spot_search["count"] or 1)))
        * 100,

        "feedback_closed": feedback_closed["count"],
        "feedback_closed_percentage": (
            1 - (feedback_closed["count"] / (dislikes["count"] or 1))
        )
        * 100,
        "reverted": reverted["count"],
        "reverted_percentage": (1 - (reverted["count"] / (spot_search["count"] or 1)))* 100,

        "total_rates": total_rates["count"],
        "total_rates_percentage": (1 - (total_rates["count"] / (spot_search["count"] or 1)))* 100,

        "feedback_spot_search": feedback_spot_search["count"],
        "feedback_spot_search_percentage": (1 - (feedback_spot_search["count"] / (rates_shown["count"] or 1)))* 100,

        "feedback_checkout": feedback_checkout["count"],
        "feedback_checkout_percentage": (1 - (feedback_checkout["count"] / (spot_search["count"] or 1)))* 100,

        "feedback_shipments": feedback_shipments["count"],
        "feedback_shipments_percentage": (1 - (feedback_shipments["count"] / (feedback_checkout["count"] or 1)))* 100,

        "feedback_cancelled_shipments": feedback_cancelled_shipments["count"],
        "feedback_cancelled_shipments": (1 - (feedback_cancelled_shipments["count"] / shipments["count"] or 1))
        * 100,
        "feedback_aborted_shipments": feedback_aborted_shipments["count"],
        "feedback_aborted_shipments": (1 - (feedback_aborted_shipments["count"] / shipments["count"] or 1))
        * 100,
        "feedback_received_shipments": feedback_received_shipments["count"],
        "feedback_received_shipments": (1 - (feedback_received_shipments["count"] / shipments["count"] or 1))
        * 100,
        "feedback_confirmed_by_importer_exporter_shipments": feedback_confirmed_by_importer_exporter_shipments["count"],
        "feedback_confirmed_by_importer_exporter_shipments": (1 - (feedback_confirmed_by_importer_exporter_shipments["count"] / shipments["count"] or 1))
        * 100,
        "feedback_completed_shipments": feedback_completed_shipments["count"],
        "feedback_completed_shipments": (1 - (feedback_completed_shipments["count"] / shipments["count"] or 1))
        * 100,
        #Checkout branch 
        "spot_search": spot_search["count"],
        "spot_search_percentage": (1 - (spot_search["count"] / (rates_shown["count"] or 1)))* 100,

        "checkout": checkout["count"],
        "checkout_percentage": (1 - (checkout["count"] / (spot_search["count"] or 1)))* 100,

        "shipments": shipments["count"],
        "shipments_percentage": (1 - (shipments["count"] / (checkout["count"] or 1)))* 100,

        "revenue_desk_shown_rates": revenue_desk_shown_rates["count"],
        "revenue_desk_shown_rates_percentage": (1 - (revenue_desk_shown_rates["count"] / (shipments["count"] or 1)))* 100,
        
        "so1_select": so1_select["count"],
        "so1_select_percentage": (
            1 - (so1_select["count"] / (revenue_desk_shown_rates["count"] or 1)))* 100,

        "revenue_desk_selected_rates": revenue_desk_selected_rates["count"],
        "revenue_desk_selected_rates_percentage": (1 - (revenue_desk_selected_rates["count"] / (shipments["count"] or 1)))* 100,
        
        "cancelled_shipments": cancelled_shipments["count"],
        "cancelled_shipments": (1 - (cancelled_shipments["count"] / shipments["count"] or 1))
        * 100,
        "aborted_shipments": aborted_shipments["count"],
        "aborted_shipments": (1 - (aborted_shipments["count"] / shipments["count"] or 1))
        * 100,
        "received_shipments": received_shipments["count"],
        "received_shipments": (1 - (received_shipments["count"] / shipments["count"] or 1))
        * 100,
        "confirmed_by_importer_exporter_shipments": confirmed_by_importer_exporter_shipments["count"],
        "confirmed_by_importer_exporter_shipments": (1 - (confirmed_by_importer_exporter_shipments["count"] / shipments["count"] or 1))
        * 100,
        "completed_shipments": completed_shipments["count"],
        "completed_shipments": (1 - (completed_shipments["count"] / shipments["count"] or 1))
        * 100,

        #Missing
        "missing_rates": missing_rates["count"],
        "missing_rates_percentage": (
            1 - (missing_rates["count"] / (spot_search["count"] or 1))
        )
        * 100,
        "closed_requests": closed_requests["count"],
        "closed_requests_percentage": (1 - (closed_requests["count"] / rates_shown["count"] or 1))
        * 100,
        "missing_reverted": missing_reverted["count"],
        "missing_reverted_percentage": (1 - (missing_reverted["count"] / rates_shown["count"] or 1))
        * 100,
        "missing_spot_search": missing_spot_search["count"],
        "missing_spot_search_percentage": (1 - (missing_spot_search["count"] / (rates_shown["count"] or 1)))* 100,

        "missing_checkout": missing_checkout["count"],
        "missing_checkout_percentage": (1 - (missing_checkout["count"] / (missing_spot_search["count"] or 1)))* 100,

        "missing_shipments": missing_shipments["count"],
        "missing_shipments_percentage": (1 - (missing_shipments["count"] / (missing_checkout["count"] or 1)))* 100,

        "missing_cancelled_shipments": missing_cancelled_shipments["count"],
        "missing_cancelled_shipments": (1 - (missing_cancelled_shipments["count"] / shipments["count"] or 1))
        * 100,
        "missing_aborted_shipments": missing_aborted_shipments["count"],
        "missing_aborted_shipments": (1 - (missing_aborted_shipments["count"] / shipments["count"] or 1))
        * 100,
        "missing_received_shipments": missing_received_shipments["count"],
        "missing_received_shipments": (1 - (missing_received_shipments["count"] / shipments["count"] or 1))
        * 100,
        "missing_confirmed_by_importer_exporter_shipments": missing_confirmed_by_importer_exporter_shipments["count"],
        "missing_confirmed_by_importer_exporter_shipments": (1 - (missing_confirmed_by_importer_exporter_shipments["count"] / shipments["count"] or 1))
        * 100,
        "missing_completed_shipments": missing_completed_shipments["count"],
        "missing_completed_shipments": (1 - (missing_completed_shipments["count"] / shipments["count"] or 1))
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
