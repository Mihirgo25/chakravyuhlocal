from services.bramhastra.client import ClickHouse
from fastapi.encoders import jsonable_encoder
from services.bramhastra.helpers.air_freight_filter_helper import (
    get_direct_indirect_filters,
)
from datetime import datetime, timedelta
from services.bramhastra.enums import AirSources

ALLOWED_TIME_PERIOD = 6


def get_air_freight_rate_trends(filters):
    where = get_direct_indirect_filters(filters)
    
    response = get_standard_price_trend(filters, where)
    
    return {
        "rate_trend": response
    }
    


def get_standard_price_trend(filters, where):
    clickhouse = ClickHouse()
    
    queries = [
        """SELECT source,toDate(day) AS day,AVG(abs(standard_price)*sign) AS average_price FROM (SELECT arrayJoin(range(toUInt32(validity_start), toUInt32(validity_end) - 1)) AS day,standard_price,source,sign FROM brahmastra.air_freight_rate_statistics"""
    ]

    if where:
        queries.append(" WHERE ")
        queries.append(where)
        queries.append("AND is_deleted = false")

    queries.append(
        """) WHERE (day <= %(end_date)s) AND (day >= %(start_date)s) GROUP BY source,day ORDER BY day,source;"""
    )

    charts = jsonable_encoder(clickhouse.execute(" ".join(queries), filters))

    return format_charts(charts, filters.get("source"))


def format_charts(charts, mode=None):
    if mode:
        NEEDED_MODES = {mode}
    else:
        NEEDED_MODES = [i.value for i in AirSources]

    return format_response(charts, NEEDED_MODES)


def format_response(response, needed_modes):
    def get_average_for_mode(response, day, mode):
        valid_values = [
            entry["average_price"] for entry in response if entry["source"] == mode
        ]
        if not valid_values:
            return None

        return sum(valid_values) / len(valid_values)

    formatted_response = []
    response_dict = {}
    for entry in response:
        day = datetime.strptime(entry["day"], "%Y-%m-%d")
        response_dict[day] = response_dict.get(day, {})
        response_dict[day].update({entry["source"]: entry["average_price"]})

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
