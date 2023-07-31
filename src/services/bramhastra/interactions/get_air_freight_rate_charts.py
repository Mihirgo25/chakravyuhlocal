from services.bramhastra.helpers.get_fcl_freight_rate_helper import ClickHouse#####common
from fastapi.encoders import jsonable_encoder
from services.bramhastra.helpers.filter_helper import (
    get_direct_indirect_filters,
)
import math


def get_air_freight_rate_charts(filters):
    where = get_direct_indirect_filters(filters)
    accuracy = get_accuracy(filters.copy(), where)
    deviation = get_deviation(filters.copy(), where)
    spot_search_to_checkout_count = get_spot_search_to_checkout_count(
        filters.copy(), where
    )
    rate_count_with_deviation_more_than_30 = get_rate_count_with_deviation_more_than_30(
        filters.copy(), where
    )
    return dict(
        accuracy=accuracy,
        deviation=deviation,
        **rate_count_with_deviation_more_than_30,
        **spot_search_to_checkout_count,
    )


def get_accuracy(filters, where):
    clickhouse = ClickHouse()
    queries = [
        """SELECT source,toDate(day) AS day,AVG(abs(accuracy)) AS average_accuracy FROM (SELECT arrayJoin(range(toUInt32(validity_start), toUInt32(validity_end) - 1)) AS day,accuracy,source FROM brahmastra.air_freight_rate_statistics"""
    ]

    if where:
        queries.append(" WHERE ")
        queries.append(where)

    queries.append(""") WHERE (day <= %(end_date)s) AND (day >= %(start_date)s) GROUP BY source,day ORDER BY day,source;""")

    charts = jsonable_encoder(clickhouse.execute(" ".join(queries), filters))

    return format_charts(charts, filters.get("mode"))


def get_deviation(filters, where):
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


def get_spot_search_to_checkout_count(filters, where):
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


def get_rate_count_with_deviation_more_than_30(filters, where):
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
        NEEDED_SOURCES = ["cargo_ai", "freight_look", "manual", "predicted", "rate_sheet"]

    formatted_charts = dict(
        cargo_ai={"id": "cargo_ai", "data": []},
        freight_look={"id": "freight_look", "data": []},
        manual={"id": "manual", "data": []},
        predicted={"id": "predicted", "data": []},
        rate_sheet={"id": "rate_sheet", "data": []},
    )

    previous_day = None
    for chart in charts:
        if not previous_day:
            previous_day = chart["day"]
            needed_sources = NEEDED_SOURCES.copy()
        elif previous_day != chart["day"]:
            for source in needed_sources:
                formatted_charts[source]["data"].append(dict(x=previous_day, y=0))
            previous_day = chart["day"]
            needed_sources = NEEDED_SOURCES.copy()

        if chart["average_accuracy"]:
            formatted_charts[chart["source"]]["data"].append(
                dict(x=chart["day"], y=round(chart["average_accuracy"], 3))
            )
            needed_sources.remove(chart["source"])
        else:
            for source in needed_sources:
                formatted_charts[source]["data"].append(dict(x=chart["day"], y=0))

    return list(formatted_charts.values())
