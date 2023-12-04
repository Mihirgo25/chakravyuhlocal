from services.bramhastra.client import ClickHouse
from services.bramhastra.enums import Air
from services.bramhastra.enums import AirMapsFilter
from fastapi.encoders import jsonable_encoder
from services.bramhastra.helpers.air_freight_filter_helper import (
    set_port_code_filters_and_service_object,
)
from services.bramhastra.models.air_freight_action import AirFreightAction
from services.bramhastra.helpers.air_freight_filter_helper import (
    get_direct_indirect_filters,
)


def get_air_freight_rate_differences(filters: dict) -> dict:
    response, locations = get_rate(filters)
    response = {
        "rate_deviations": response,
        "currency": filters.get("currency") or Air.default_currency.value,
    }
    if locations:
        response.update(locations)
    return response


def get_rate(filters: dict) -> list:
    clickhouse = ClickHouse()

    queries = [
        f"""
            SELECT ROUND(bas_standard_price_diff_from_selected_rate) AS deviation, 
            COUNT(DISTINCT rate_id) AS count
            FROM brahmastra.{AirFreightAction._meta.table_name}
        """
    ]

    location_object = dict()

    if filters.get(AirMapsFilter.origin_airport_code.value) or filters.get(
       AirMapsFilter.destination_airport_code.value
    ):
        set_port_code_filters_and_service_object(filters, location_object)

    where = get_direct_indirect_filters(filters)

    if where:
        queries.append(" WHERE ")
        queries.append(where)

    queries.append("""GROUP BY deviation ORDER BY deviation;""")
    charts = jsonable_encoder(clickhouse.execute(" ".join(queries), filters))

    formatted_charts = format_charts(charts)

    return formatted_charts, location_object


def format_charts(charts: list) -> list:
    result_dict = dict()
    range_val = 20
    min_diff = 0
    if len(charts) > 0:
        min_diff = int(charts[0].get("deviation", "0"))

    range_min = min_diff - (min_diff % range_val)
    range_max = range_min + range_val

    result_dict[f"{range_min}_{range_max}"] = 0

    for entry in charts:
        deviation = entry.get("deviation", "0")
        rate_count = entry.get("count", "0")

        if deviation > range_max:
            range_min += range_val
            range_max += range_val
            result_dict[f"{range_min}_{range_max}"] = 0

        result_dict[f"{range_min}_{range_max}"] += rate_count

    return format_response(result_dict)


def format_response(response: list) -> list:
    formatted_response = []

    for key, val in response.items():
        [min_val, max_val] = key.split("_")
        formatted_response.append(
            {
                "from": min_val,
                "to": max_val,
                "rate_count": val,
            }
        )

    return formatted_response
