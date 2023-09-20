from services.bramhastra.client import ClickHouse
from services.bramhastra.helpers.fcl_freight_filter_helper import (
    get_direct_indirect_filters,
)
import concurrent.futures
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)

ALLOWED_TIME_PERIOD = 6

DEFAULT_AGGREGATE_SELECT = {"bas_average_price": "AVG(abs(bas_standard_price))"}

FREQUENCY_FUNCS = {"Month": "toYYYYMM", "Week": "toISOWeek"}


def list_fcl_freight_rate_trends(filters: dict) -> dict:
    where = get_direct_indirect_filters(filters, date=None)
    return get_rate(filters, where)


def get_rate(filters: dict, where: str) -> list:
    query_current, query_months, query_weeks = generate_queries(filters, where)
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(ClickHouse().execute, query_current, filters),
            executor.submit(ClickHouse().execute, query_weeks, filters),
            executor.submit(ClickHouse().execute, query_months, filters)
        ]
        for i in range(0, len(futures)):
            results.append(futures[i].result())
    response = {
        "current_price": results[0][0] if results[0] else results[0],
        "weeks": results[1],
        "months": results[2],
    }
    return response


def generate_queries(filters, where):
    queries = []
    query_present = [
        f"""SELECT bas_standard_price FROM brahmastra.{FclFreightRateStatistic._meta.table_name} WHERE is_deleted = false"""
    ]
    if where:
        query_present.append(f"AND {where}")
    query_present.append("ORDER BY rate_updated_at DESC LIMIT 1")
    queries.append(" ".join(query_present))
    for time_unit, details in filters.get("frequency", {}).items():
        queries.append(get_query(time_unit, details, where))
    return queries


def get_query(time_unit, details, where):
    query = [
        f"""SELECT {FREQUENCY_FUNCS.get(time_unit)}(rate_created_at) AS {time_unit},AVG(bas_standard_price) AS average_bas_standard_price FROM brahmastra.{FclFreightRateStatistic._meta.table_name} WHERE is_deleted = false"""
    ]
    if where:
        query.append(f"AND {where}")
    if "before" in details:
        query.append(query_before(details.get("before"), time_unit, details["unit"]))
    elif "after" in details:
        query.append(query_after(details.get("after"), time_unit, details["unit"]))
    query.append(
        f"""GROUP BY {time_unit} ORDER BY {time_unit} ASC"""
    )
    return " ".join(query)


def query_after(startDate, timeUnit, unit):
    return f""" AND (toDate(rate_created_at) >= ('{startDate}')) AND (toDate(rate_created_at) <= add{timeUnit}s(toDate('{startDate}'), {unit-1})) """


def query_before(endDate, timeUnit, unit):
    return f""" AND (toDate(rate_created_at) <= ('{endDate}')) AND (toDate(rate_created_at) >= subtract{timeUnit}s(toDate('{endDate}'), {unit-1})) """
