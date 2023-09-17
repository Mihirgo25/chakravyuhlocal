from services.bramhastra.client import ClickHouse
from services.bramhastra.enums import FclParentMode, Fcl
from services.bramhastra.enums import MapsFilter
from fastapi.encoders import jsonable_encoder
from services.bramhastra.helpers.fcl_freight_filter_helper import (
    set_port_code_filters_and_service_object,
)
from services.bramhastra.helpers.fcl_freight_filter_helper import (
    get_direct_indirect_filters,
)

def get_fcl_freight_rate_deviations(filters: dict) -> dict:
    response, locations = get_rate(filters)
    response = {
        "rate_deviations": response,
        "currency": filters.get("currency") or Fcl.default_currency.value,
    }
    if locations:
        response.update(locations)
    return response

def get_rate(filters: dict) -> list:
    clickhouse = ClickHouse()

    queries = [
        f"""SELECT ROUND(bas_standard_price_diff_from_selected_rate) AS deviation, COUNT(rate_id) AS count FROM brahmastra.fcl_freight_actions"""
    ]

    location_object = dict()

    if filters.get(MapsFilter.origin_port_code.value) or filters.get(
        MapsFilter.destination_port_code.value
    ):
        set_port_code_filters_and_service_object(filters, location_object)
        
    where = get_direct_indirect_filters(filters)

    if where:
        queries.append(" WHERE ")
        queries.append(where)
        queries.append("AND is_deleted = false")
        
    queries.append(
        """) WHERE (day <= %(end_date)s) AND (day >= %(start_date)s) GROUP BY parent_mode,day ORDER BY day,mode;"""
    )

    queries.append(
        """ GROUP BY ROUND(bas_standard_price_diff_from_selected_rate) """
    )

    charts = jsonable_encoder(clickhouse.execute(" ".join(queries), filters))

    formatted_charts = format_charts(charts, filters)

    return formatted_charts, location_object

def format_charts(charts: list, filters: dict) -> list:
    NEEDED_MODES = {filters.get("mode")} if filters.get("mode") else {i.value for i in FclParentMode}

    return format_response(charts, filters, NEEDED_MODES)

def format_response(response: list) -> list:
    formatted_response = []
    for entry in response:
        formatted_response.append({
            'deviation': entry.get('rate', '0'),
            'count': entry.get('count','0'),
        })

    return formatted_response
