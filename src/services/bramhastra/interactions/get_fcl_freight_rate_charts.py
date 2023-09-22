from services.bramhastra.client import ClickHouse
from fastapi.encoders import jsonable_encoder
from services.bramhastra.helpers.fcl_freight_filter_helper import (
    get_direct_indirect_filters,
)
import math
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from database.db_session import rd
from services.bramhastra.enums import RedisKeys, FclParentMode
import concurrent.futures
from services.bramhastra.models.fcl_freight_action import FclFreightAction
import sys

ALLOWED_TIME_PERIOD = 6

MAX_ALLOWABLE_DEFAULT_BAS_DIFF = 100

from services.bramhastra.interactions.get_fcl_freight_rate_differences import (
    get_fcl_freight_rate_differences,
)

def get_fcl_freight_rate_charts(filters):
    where = get_direct_indirect_filters(filters)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        accuracy_future = executor.submit(get_accuracy, filters, where)
        rates_affected_future = executor.submit(get_rates_affected, filters, where)
        spot_search_future = executor.submit(
            get_spot_search_to_checkout_count, filters, where
        )
        rate_count_future = executor.submit(
            get_rate_count_with_deviation_more_than_x_price, filters, where
        )

    resp = dict(
        rates_affected=rates_affected_future.result(),
        **rate_count_future.result(),
        **spot_search_future.result(),
    )

    chart_type = filters.get('chart_type')
    match chart_type:
        case 'deviation':
            resp['deviation'] = get_fcl_freight_rate_differences(filters)
        
        case 'accuracy':
            resp['accuracy'] = accuracy_future.result()
    
    return jsonable_encoder(resp)


def get_accuracy(filters, where):
    if is_json_needed(filters):
        if url := get_link():
            return url

    clickhouse = ClickHouse()
    queries = [
        f"""SELECT parent_mode as mode,toDate(updated_at) AS day,AVG(abs(bas_standard_price_accuracy)*sign) AS average_accuracy FROM brahmastra.{FclFreightAction._meta.table_name}"""
    ]
    
    queries.append(" WHERE ")

    if where:
        queries.append(where)
        queries.append(f"AND bas_standard_price_accuracy != {sys.float_info.max}")

    queries.append(
        """GROUP BY parent_mode,day ORDER BY day,mode;"""
    )

    charts = jsonable_encoder(clickhouse.execute(" ".join(queries), filters))

    return format_charts(charts, filters.get("mode"))


def get_rates_affected(filters, where):
    clickhouse = ClickHouse()

    query = [
        f"""SELECT toStartOfHour(rate_updated_at) AS time,COUNT(*) as rates_count FROM brahmastra.{FclFreightAction._meta.table_name}"""
    ]

    if where:
        query.append(f"WHERE {where}")

    query.append("GROUP BY time ORDER BY time ASC")

    return clickhouse.execute(" ".join(query), filters)


def get_spot_search_to_checkout_count(filters, where):
    clickhouse = ClickHouse()

    queries = [
        f"""SELECT FLOOR((1 - SUM(checkout)/COUNT(DISTINCT spot_search_id)),2)*100 as spot_search_to_checkout_count from brahmastra.{FclFreightAction._meta.table_name}"""
    ]

    if where:
        queries.append(" WHERE ")
        queries.append(where)

    statistics = clickhouse.execute(" ".join(queries), filters)[0]

    if math.isnan(statistics["spot_search_to_checkout_count"]):
        statistics["spot_search_to_checkout_count"] = 0

    return statistics


def get_rate_count_with_deviation_more_than_x_price(filters, where):
    clickhouse = ClickHouse()

    queries = [
        f"""SELECT count(DISTINCT rate_id) as rate_count_with_deviation_more_than_x_price from brahmastra.{FclFreightAction._meta.table_name} WHERE ABS(bas_standard_price_diff_from_selected_rate) >= {MAX_ALLOWABLE_DEFAULT_BAS_DIFF}"""
    ]

    if where:
        queries.append(" AND ")
        queries.append(where)

    return clickhouse.execute(" ".join(queries), filters)[0]


def format_charts(charts, mode=None):
    if mode:
        NEEDED_MODES = {mode}
    else:
        NEEDED_MODES = [i.value for i in FclParentMode]

    return format_response(charts, NEEDED_MODES)


def format_response(response, needed_modes):
    def get_average_for_mode(response, day, mode):
        valid_values = [
            entry["average_accuracy"] for entry in response if entry["mode"] == mode
        ]
        if not valid_values:
            return None

        return sum(valid_values) / len(valid_values)

    formatted_response = []
    response_dict = {}
    for entry in response:
        day = datetime.strptime(entry["day"], "%Y-%m-%d")
        response_dict[day] = response_dict.get(day, {})
        response_dict[day].update({entry["mode"]: entry["average_accuracy"]})

    for day, values in sorted(response_dict.items()):
        data_object = {"day": day.timestamp() * 1000}
        for mode in needed_modes:
            if mode in values:
                data_object[mode] = values[mode]
            else:
                prev_day = day - timedelta(days=1)
                next_day = day + timedelta(days=1)

                prev_value = get_average_for_mode(response, prev_day, mode)
                next_value = get_average_for_mode(response, next_day, mode)

                if prev_value is not None and next_value is not None:
                    data_object[mode] = (prev_value + next_value) / 2
                elif prev_value is not None:
                    data_object[mode] = prev_value
                elif next_value is not None:
                    data_object[mode] = next_value

        formatted_response.append(data_object)

    return formatted_response


def is_json_needed(filters):
    start_date = (
        datetime.strptime(filters.get("start_date"), "%Y-%m-%d")
        if isinstance(filters.get("start_date"), str)
        else filters.get("start_date")
    )
    end_date = (
        datetime.strptime(filters.get("end_date"), "%Y-%m-%d")
        if isinstance(filters.get("end_date"), str)
        else filters.get("end_date")
    )
    duration = relativedelta(end_date, start_date)
    return duration.months > 6


def get_link():
    return rd.get(RedisKeys.fcl_freight_rate_all_time_accuracy_chart.value)
