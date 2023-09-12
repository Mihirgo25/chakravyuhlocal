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

    statistics = [
        [
            {
                "action_type": "checkout",
                "rates_count": lifecycle_statistics["checkout"],
                "drop": filter_out_of_range_value(
                    lifecycle_statistics["checkout_percentage"]
                ),
            },
            {
                "action_type": "booking_confirm",
                "rates_count": lifecycle_statistics["booking_confirm"],
                "drop": filter_out_of_range_value(
                    lifecycle_statistics["booking_confirm_percentage"]
                ),
            },
            {
                "action_type": "revenue_desk",
                "rates_count": lifecycle_statistics["revenue_desk_visit"],
                "drop": filter_out_of_range_value(
                    lifecycle_statistics["revenue_desk_visit_percentage"]
                ),
            },
            {
                "action_type": "so1",
                "rates_count": lifecycle_statistics["so1_visit"],
                "drop": filter_out_of_range_value(
                    lifecycle_statistics["so1_visit_percentage"]
                ),
            },
        ],
        [
            {
                "action_type": "missing_rates",
                "rates_count": lifecycle_statistics["missing_rates"],
                "drop": filter_out_of_range_value(
                    lifecycle_statistics["missing_rates_percentage"]
                ),
            },
            {
                "action_type": "rates_triggered",
                "rates_count": lifecycle_statistics["missing_rates_reverted"],
                "drop": filter_out_of_range_value(
                    lifecycle_statistics["missing_rates_reverted_percentage"]
                ),
            },
        ],
        [
            {
                "action_type": "dislike",
                "rates_count": lifecycle_statistics["dislikes"],
                "drop": filter_out_of_range_value(
                    lifecycle_statistics["dislikes_percentage"]
                ),
            },
            {
                "action_type": "feedback_received",
                "rates_count": lifecycle_statistics["feedback_recieved"],
                "drop": filter_out_of_range_value(
                    lifecycle_statistics["feedback_recieved_percentage"]
                ),
            },
            {
                "action_type": "rates_reverted",
                "rates_count": lifecycle_statistics["dislikes_rates_reverted"],
                "drop": filter_out_of_range_value(
                    lifecycle_statistics["dislikes_rates_reverted_percentage"]
                ),
            },
        ],
        [
            {
                "action_type": "idle_rates",
                "rates_count": lifecycle_statistics["idle_rates"],
                "drop": lifecycle_statistics["idle_rates_percentage"],
            },
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
    rates = [
        f"""
        SELECT COUNT(DISTINCT rate_id) AS count FROM brahmastra.{FclFreightRateStatistic._meta.table_name} WHERE is_deleted = false
        """
    ]
    
    spot_search = [count_distinct_by_rate_id_query('spot_search_count')]
    checkout = [count_distinct_by_rate_id_query('checkout_count')]
    revenue_desk_visit = [count_distinct_by_rate_id_query('revenue_desk_visit_count')]
    so1_visit = [count_distinct_by_rate_id_query('so1_visit_count')]
    booking_confirm = [count_distinct_by_rate_id_query('shipment_confirmed_by_importer_exporter_count')]
    dislikes = [count_distinct_by_rate_id_query('dislikes_count')]
    feedback_recieved = [count_distinct_by_rate_id_query('feedback_recieved_count')]

    dislikes_rates_reverted = [
        f"""
        SELECT COUNT(DISTINCT rate_id) AS count from brahmastra.{FclFreightRateStatistic._meta.table_name} WHERE source = '{FclModes.missing_rate.value}'
        """
    ]

    missing_rates = [
        f"""
       SELECT COUNT(DISTINCT rate_request_id) AS count from brahmastra.{FclFreightRateRequestStatistic._meta.table_name} WHERE is_rate_reverted = false
       """
    ]

    missing_rates_reverted = [
        f"""
        SELECT COUNT(DISTINCT rate_id) AS count from brahmastra.{FclFreightRateStatistic._meta.table_name} WHERE source = '{FclModes.missing_rate.value}'
        """
    ]

    idle_rates = [
        f"""
        SELECT COUNT(DISTINCT rate_id) as count FROM brahmastra.{FclFreightRateStatistic._meta.table_name} WHERE spot_search_count = 0 AND checkout_count = 0 AND dislikes_count = 0 AND likes_count = 0
        """
    ]
    
    rate_shown = [
        f"""
        SELECT SUM(spot_search) AS count FROM brahmastra.{FclFreightAction._meta.table_name} WHERE spot_search > 0
        """ 
    ]

    action_spot_search = [
        f"""
        SELECT COUNT(DISTINCT spot_search_id) AS count FROM brahmastra.{FclFreightAction._meta.table_name} WHERE spot_search = 1
        """
    ]
    

    action_checkout = [generate_sum_query("checkout")]
    shipments = [generate_sum_query("shipment")]
    so1_select = [generate_sum_query("so1_select")]
    revenue_desk_shown_rates = [generate_sum_query("revenue_desk_visit")]

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
    
    action_likes = [count_boolean_query('liked')]
    actions_dislikes = [count_boolean_query('disliked')]

    feedback_closed = [
        f"""
        SELECT COUNT(*) AS count FROM brahmastra.{FclFreightAction._meta.table_name} WHERE status = 'inactive'
        """
    ]
    reverted = [
        f"""
        SELECT SUM(is_reverted) AS count FROM brahmastra.{FclFreightRateRequest._meta.table_name} WHERE is_reverted = 1 GROUP BY rate_id
        """
    ]
    rate_requests= [
        f"""
        SELECT COUNT(DISTINCT rate_id) AS count FROM brahmastra.{FclFreightRateRequest._meta.table_name} WHERE column_status = 'inactive'
        """
    ]
    closed_requests = [
        f"""
        SELECT COUNT(*) AS count FROM brahmastra.{FclFreightRateRequest._meta.table_name} WHERE status = 'inactive'
        """
    ]


    if where:
        rates.append(f"AND {where}")
        spot_search.append(f"AND {where}")
        checkout.append(f"AND {where}")
        booking_confirm.append(f"AND {where}")
        revenue_desk_visit.append(f"AND {where}")
        so1_visit.append(f"AND {where}")
        dislikes.append(f"AND {where}")
        feedback_recieved.append(f"AND {where}")
        dislikes_rates_reverted.append(f"AND {where}")
        missing_rates_reverted.append(f"AND {where}")
        idle_rates.append(f"AND {where}")

    missing_rates_filter = filters.copy()

    missing_rates_where = get_direct_indirect_filters_for_rate_request(
        missing_rates_filter
    )

    if missing_rates_where:
        missing_rates.append(f"AND {missing_rates_where}")

    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(ClickHouse().execute, " ".join(rates), filters),
            executor.submit(ClickHouse().execute, " ".join(spot_search), filters),
            executor.submit(ClickHouse().execute, " ".join(checkout), filters),
            executor.submit(ClickHouse().execute, " ".join(booking_confirm), filters),
            executor.submit(
                ClickHouse().execute, " ".join(revenue_desk_visit), filters
            ),
            executor.submit(ClickHouse().execute, " ".join(so1_visit), filters),
            executor.submit(ClickHouse().execute, " ".join(dislikes), filters),
            executor.submit(ClickHouse().execute, " ".join(feedback_recieved), filters),
            executor.submit(
                ClickHouse().execute, " ".join(dislikes_rates_reverted), filters
            ),
            executor.submit(ClickHouse().execute, " ".join(missing_rates), filters),
            executor.submit(
                ClickHouse().execute, " ".join(missing_rates_reverted), filters
            ),
            executor.submit(ClickHouse().execute, " ".join(idle_rates), filters),
        ]
        for i in range(0, len(futures)):
            results.append(futures[i].result()[0])

    rates = results[0]
    spot_search = results[1]
    checkout = results[2]
    booking_confirm = results[3]
    revenue_desk_visit = results[4]
    so1_visit = results[5]
    dislikes = results[6]
    feedback_recieved = results[7]
    dislikes_rates_reverted = results[8]
    missing_rates = results[9]
    missing_rates_reverted = results[10]
    idle_rates = results[11]

    lifecycle_statistics = {
        "rates": rates["count"],
        "spot_search": spot_search["count"],
        "spot_search_percentage": (1 - (spot_search["count"] / (rates["count"] or 1)))
        * 100,
        "checkout": checkout["count"],
        "checkout_percentage": (1 - (checkout["count"] / (spot_search["count"] or 1)))
        * 100,
        "booking_confirm": booking_confirm["count"],
        "booking_confirm_percentage": (
            1 - (booking_confirm["count"] / (checkout["count"] or 1))
        )
        * 100,
        "revenue_desk_visit": revenue_desk_visit["count"],
        "revenue_desk_visit_percentage": (
            1 - (revenue_desk_visit["count"] / (booking_confirm["count"] or 1))
        )
        * 100,
        "so1_visit": so1_visit["count"],
        "so1_visit_percentage": (
            1 - (so1_visit["count"] / (revenue_desk_visit["count"] or 1))
        )
        * 100,
        "dislikes": dislikes["count"],
        "dislikes_percentage": (1 - (dislikes["count"] / (spot_search["count"] or 1)))
        * 100,
        "feedback_recieved": feedback_recieved["count"],
        "feedback_recieved_percentage": (
            1 - (feedback_recieved["count"] / (dislikes["count"] or 1))
        )
        * 100,
        "dislikes_rates_reverted": dislikes_rates_reverted["count"],
        "dislikes_rates_reverted_percentage": (
            1 - (dislikes_rates_reverted["count"] / (spot_search["count"] or 1))
        )
        * 100,
        "missing_rates": missing_rates["count"],
        "missing_rates_percentage": (
            1 - (missing_rates["count"] / (spot_search["count"] or 1))
        )
        * 100,
        "missing_rates_reverted": missing_rates_reverted["count"],
        "missing_rates_reverted_percentage": (
            1 - (missing_rates_reverted["count"] / (missing_rates["count"] or 1))
        )
        * 100,
        "idle_rates": idle_rates["count"],
        "idle_rates_percentage": (1 - (idle_rates["count"] / rates["count"] or 1))
        * 100,
    }
    return lifecycle_statistics


async def get_mode_wise_rate_count(filters, where):
    clickhouse = ClickHouse()

    queries = [
        """SELECT parent_mode,COUNT(DISTINCT rate_id) as rate_count from brahmastra.fcl_freight_rate_statistics"""
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
def count_boolean_query(column):
        return f"""
        SELECT SUM({column}) AS count FROM brahmastra.{FclFreightAction._meta.table_name} WHERE {column} = 1
        """

def count_distinct_by_rate_id_query(column):
        return f"""
        SELECT COUNT(DISTINCT rate_id) AS count FROM brahmastra.{FclFreightRateStatistic._meta.table_name} WHERE {column}> 0
        """