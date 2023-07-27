from services.bramhastra.helpers.get_fcl_freight_rate_helper import ClickHouse
from fastapi.encoders import jsonable_encoder
from services.bramhastra.helpers.filter_helper import (
    get_direct_indirect_filters,
    NEEDED_MODES,
)


async def get_fcl_freight_rate_charts(filters):
    where = get_direct_indirect_filters(filters)
    accuracy = await get_accuracy(filters.copy(), where)
    deviation = await get_deviation(filters.copy(), where)
    spot_search_to_checkout_count = await get_spot_search_to_checkout_count(
        filters.copy(), where
    )
    rate_count_with_deviation_more_than_30 = (
        await get_rate_count_with_deviation_more_than_30(filters.copy(), where)
    )

    return dict(
        accuracy=accuracy,
        deviation=deviation,
        **rate_count_with_deviation_more_than_30,
        **spot_search_to_checkout_count,
    )


async def get_accuracy(filters, where):
    clickhouse = ClickHouse()
    queries = ["""SELECT mode,toDate(day) AS day,AVG(abs(accuracy)) AS average_accuracy FROM (SELECT arrayJoin(range(toUInt32(validity_start), toUInt32(validity_end) - 1)) AS day,accuracy,mode FROM brahmastra.fcl_freight_rate_statistics"""]

    if where:
        queries.append(" WHERE ")
        queries.append(where)

    queries.append(""") GROUP BY mode,day ORDER BY day,mode;""")

    charts = jsonable_encoder(clickhouse.execute(" ".join(queries), filters))

    return format_charts(charts)


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
            FROM brahmastra.fcl_freight_rate_statistics"""
    ]

    if where:
        queries.append(" WHERE ")
        queries.append(where)

    queries.append("GROUP BY range ORDER BY range WITH FILL FROM -80 TO 100 STEP 20;")

    response = clickhouse.execute(" ".join(queries), filters)

    return [i for i in response if i["range"] or i["range"] == 0]


async def get_spot_search_to_checkout_count(filters, where):
    clickhouse = ClickHouse()

    queries = ["""SELECT FLOOR(AVG(1 - checkout_count/spot_search_count),2)*100 as spot_search_to_checkout_count from brahmastra.fcl_freight_rate_statistics"""]

    if where:
        queries.append(" WHERE ")
        queries.append(where)

    return clickhouse.execute(" ".join(queries), filters)[0]


async def get_rate_count_with_deviation_more_than_30(filters, where):
    clickhouse = ClickHouse()

    queries = ["""SELECT count(id) as rate_count_with_deviation_more_than_30 from brahmastra.fcl_freight_rate_statistics WHERE rate_deviation_from_booking_rate > 30"""]

    if where:
        queries.append(" AND ")
        queries.append(where)

    return clickhouse.execute(" ".join(queries), filters)[0]


def format_charts(charts):
    formatted_charts = dict(
        manual={"id": "supply_rates", "data": []},
        rate_extension={"id": "rate_extension", "data": []},
        cluster_extension={"id": "cluster_extension", "data": []},
        predicted={"id": "predicted", "data": []},
    )

    previous_day = None
    for chart in charts:
        if not previous_day:
            previous_day = chart["day"]
            needed_modes = NEEDED_MODES.copy()
        elif previous_day != chart["day"]:
            for mode in needed_modes:
                formatted_charts[mode]["data"].append(dict(x=previous_day, y=0))
            previous_day = chart["day"]
            needed_modes = NEEDED_MODES.copy()

        if chart["average_accuracy"]:
            formatted_charts[chart["mode"]]["data"].append(
                dict(x=chart["day"], y=round(chart["average_accuracy"], 3))
            )
            needed_modes.remove(chart["mode"])
        else:
            for mode in needed_modes:
                formatted_charts[mode]["data"].append(dict(x=chart["day"], y=0))

    return list(formatted_charts.values())