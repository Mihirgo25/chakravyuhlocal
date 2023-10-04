from services.bramhastra.client import ClickHouse
from fastapi.encoders import jsonable_encoder
from services.bramhastra.helpers.fcl_freight_filter_helper import (
    get_direct_indirect_filters,
)
from datetime import datetime, timedelta
from services.bramhastra.enums import FclParentMode, Fcl
from micro_services.client import common
from services.bramhastra.helpers.fcl_freight_filter_helper import (
    set_port_code_filters_and_service_object,
)
from services.bramhastra.enums import MapsFilter

ALLOWED_TIME_PERIOD = 6

DEFAULT_AGGREGATE_SELECT = {
    "average_price": "(SUM(standard_price*sign)/COUNT(DISTINCT id))",
    "min_price": "MIN(standard_price)",
    "max_price": "MAX(standard_price)",
}

ALLOWED_FREQUENCY_TYPES = {
    "year": "toStartOfMonth(toDate(day))",
    "month": "toStartOfMonth(toDate(day))",
    "week": "toStartOfWeek(toDate(day))",
    "day": "toDate(day)",
}


def get_fcl_freight_rate_trends(filters: dict) -> dict:
    response, locations = get_rate(filters)
    response = {
        "rate_trend": response,
        "currency": filters.get("currency") or Fcl.default_currency.value,
    }
    if locations:
        response.update(locations)
    return response


def get_rate(filters: dict) -> list:
    clickhouse = ClickHouse()

    aggregate_select = ",".join(
        [
            f"{v} AS {k}"
            for k, v in filters.get(
                "aggregate_select", DEFAULT_AGGREGATE_SELECT
            ).items()
        ]
    )

    interval = ALLOWED_FREQUENCY_TYPES[filters.get("frequency", "day")]

    queries = [
        f"""SELECT parent_mode as mode,{interval} AS day,{aggregate_select} FROM (SELECT arrayJoin(range(toUInt32(validity_start), toUInt32(validity_end) - 1)) AS day,standard_price,parent_mode,sign,id FROM brahmastra.fcl_freight_rate_statistics"""
    ]

    location_object = dict()

    if filters.get(MapsFilter.origin_port_code.value) or filters.get(
        MapsFilter.destination_port_code.value
    ):
        set_port_code_filters_and_service_object(filters, location_object)

    where = get_direct_indirect_filters(filters, date=None)

    if where:
        queries.append(" WHERE ")
        queries.append(where)
        queries.append("AND is_deleted = false")

    queries.append(
        """) WHERE (day <= %(end_date)s) AND (day >= %(start_date)s) GROUP BY parent_mode,day ORDER BY day,mode;"""
    )

    charts = jsonable_encoder(clickhouse.execute(" ".join(queries), filters))

    formatted_charts = format_charts(charts, filters)

    return formatted_charts, location_object


def format_charts(charts: list, filters: dict) -> list:
    NEEDED_MODES = (
        {filters.get("mode")}
        if filters.get("mode")
        else {i.value for i in FclParentMode}
    )

    return format_response(charts, filters, NEEDED_MODES)


def format_response(response: list, filters: dict, needed_modes: list) -> list:
    def get_average_for_mode(response, day, mode):
        valid_values = [
            entry["average_price"]
            for entry in response
            if entry["mode"] == mode and entry["day"] == day
        ]
        if not valid_values:
            return None

        return sum(valid_values) / len(valid_values)

    formatted_response = []
    response_dict = {}
    for entry in response:
        day = datetime.strptime(entry["day"], "%Y-%m-%d")
        response_dict[day] = response_dict.get(day, {})
        response_dict[day].update(
            {entry["mode"]: {k: entry[k] for k in DEFAULT_AGGREGATE_SELECT}}
        )

    exchange_rate = 1

    if (
        filters.get("currency")
        and filters.get("currency") != Fcl.default_currency.value
    ):
        exchange_rate = common.get_exchange_rate(
            {
                "from_currency": Fcl.default_currency.value,
                "to_currency": filters.get("currency"),
            }
        )

    for day, values in sorted(response_dict.items()):
        if filters.get("currency"):
            for mode, aggregate_values in values.items():
                for key in DEFAULT_AGGREGATE_SELECT.keys():
                    aggregate_values[key] = aggregate_values[key] * exchange_rate

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
                    data_object[mode] = {
                        k: (prev_value + next_value) / 2
                        for k in DEFAULT_AGGREGATE_SELECT
                    }
                elif prev_value is not None:
                    data_object[mode] = {
                        k: prev_value for k in DEFAULT_AGGREGATE_SELECT
                    }
                elif next_value is not None:
                    data_object[mode] = {
                        k: next_value for k in DEFAULT_AGGREGATE_SELECT
                    }

        formatted_response.append(data_object)

    return formatted_response
