from services.bramhastra.client import ClickHouse
from fastapi.encoders import jsonable_encoder
from services.bramhastra.helpers.air_freight_filter_helper import (
    get_direct_indirect_filters,
)
import math
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from database.db_session import rd
from services.bramhastra.enums import RedisKeys

ALLOWED_TIME_PERIOD = 6


async def get_air_freight_rate_charts(filters):
    where = get_direct_indirect_filters(filters)

    accuracy = await get_accuracy(filters, where)
    deviation = await get_deviation(filters, where)
    spot_search_to_checkout_count = await get_spot_search_to_checkout_count(
        filters, where
    )
    rate_count_with_deviation_more_than_30 = (
        await get_rate_count_with_deviation_more_than_30(filters, where)
    )

    return dict(
        accuracy=accuracy,
        deviation=deviation,
        **rate_count_with_deviation_more_than_30,
        **spot_search_to_checkout_count,
    )


async def get_accuracy(filters, where):
    if is_json_needed(filters):
        return get_link()

    clickhouse = ClickHouse()
    queries = [
        """SELECT source,toDate(day) AS day,AVG(abs(accuracy)*sign) AS average_accuracy FROM (SELECT arrayJoin(range(toUInt32(validity_start), toUInt32(validity_end) - 1)) AS day,accuracy,source,sign FROM brahmastra.air_freight_rate_statistics"""
    ]

    if where:
        queries.append(" WHERE ")
        queries.append(where)

    queries.append(
        """) WHERE (day <= %(end_date)s) AND (day >= %(start_date)s) GROUP BY source,day HAVING sum(sign)>0 ORDER BY day,source;"""
    )

    charts = jsonable_encoder(clickhouse.execute(" ".join(queries), filters))

    return format_charts(charts, filters.get("source"))


async def get_deviation(filters, where):
    clickhouse = ClickHouse()
    queries = [
        """SELECT CASE
                WHEN rate_deviation_from_booking_rate BETWEEN -100 AND -80 THEN -80
                WHEN rate_deviation_from_booking_rate BETWEEN -79 AND -60 THEN -60
                WHEN rate_deviation_from_booking_rate BETWEEN -59 AND -40 THEN -40
                WHEN rate_deviation_from_booking_rate BETWEEN -39 AND -20 THEN -20
                WHEN rate_deviation_from_booking_rate BETWEEN -20 AND 0 THEN 0
                WHEN rate_deviation_from_booking_rate BETWEEN 1 AND 20 THEN 20
                WHEN rate_deviation_from_booking_rate BETWEEN 21 AND 40 THEN 40
                WHEN rate_deviation_from_booking_rate BETWEEN 41 AND 60 THEN 60
                WHEN rate_deviation_from_booking_rate BETWEEN 61 AND 80 THEN 80
                WHEN rate_deviation_from_booking_rate BETWEEN 81 AND 100 THEN 100
            END AS range,
            COUNT(1) AS count
            FROM brahmastra.air_freight_rate_statistics"""
    ]

    if where:
        queries.append(" WHERE ")
        queries.append(where)

    queries.append("GROUP BY range ORDER BY range WITH FILL FROM -80 TO 100 STEP 20;")

    response = clickhouse.execute(" ".join(queries), filters)

    return [i for i in response if i["range"] or i["range"] == 0]


async def get_spot_search_to_checkout_count(filters, where):
    clickhouse = ClickHouse()

    queries = [
        """SELECT FLOOR(AVG(1 - checkout_count/spot_search_count),2)*100 as spot_search_to_checkout_count from brahmastra.air_freight_rate_statistics"""
    ]

    if where:
        queries.append(" WHERE ")
        queries.append(where)

    statistics = clickhouse.execute(" ".join(queries), filters)[0]

    if math.isnan(statistics["spot_search_to_checkout_count"]):
        statistics["spot_search_to_checkout_count"] = 0

    return statistics


async def get_rate_count_with_deviation_more_than_30(filters, where):
    clickhouse = ClickHouse()

    queries = [
        """SELECT count(id) as rate_count_with_deviation_more_than_30 from brahmastra.air_freight_rate_statistics WHERE rate_deviation_from_booking_rate > 30"""
    ]

    if where:
        queries.append(" AND ")
        queries.append(where)

    return clickhouse.execute(" ".join(queries), filters)[0]


def format_charts(charts, source=None):
    if source:
        NEEDED_SOURCES = {source}
    else:
        NEEDED_SOURCES = {
            "freight_look",
            "rate_sheet",
            "predicted",
            "cargo_ai",
        }

    return format_response(charts, NEEDED_SOURCES)


def format_response(response, needed_sources):
    def get_average_for_source(response, day, source):
        valid_values = [
            entry["average_accuracy"] for entry in response if entry["source"] == source
        ]
        if not valid_values:
            return None

        return sum(valid_values) / len(valid_values)

    formatted_response = []
    response_dict = {}
    for entry in response:
        day = datetime.strptime(entry["day"], "%Y-%m-%d")
        response_dict[day] = response_dict.get(day, {})
        response_dict[day].update({entry["source"]: entry["average_accuracy"]})

    for day, values in sorted(response_dict.items()):
        data_object = {"day": day.timestamp() * 1000}
        for source in needed_sources:
            if source in values:
                data_object[source] = values[source]
            else:
                prev_day = day - timedelta(days=1)
                next_day = day + timedelta(days=1)

                prev_value = get_average_for_source(response, prev_day, source)
                next_value = get_average_for_source(response, next_day, source)

                if prev_value is not None and next_value is not None:
                    data_object[source] = (prev_value + next_value) / 2
                elif prev_value is not None:
                    data_object[source] = prev_value
                elif next_value is not None:
                    data_object[source] = next_value

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
    return rd.get(RedisKeys.air_freight_rate_all_time_accuracy_chart.value)
