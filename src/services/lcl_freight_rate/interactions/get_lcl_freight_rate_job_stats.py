from services.lcl_freight_rate.models.lcl_freight_rate_jobs import LclFreightRateJob
import json
from libs.get_applicable_filters import get_applicable_filters
from libs.get_filters import get_filters
from libs.json_encoder import json_encoder
from datetime import datetime, timedelta
from peewee import fn
from playhouse.postgres_ext import SQL


possible_direct_filters = [
    "origin_port_id",
    "destination_port_id",
    "commodity",
    "user_id",
    "cogo_entity_id",
]
possible_indirect_filters = ["updated_at"]

uncommon_filters = ["serial_id", "status"]

STRING_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"


STATISTICS = {
    "pending": 0,
    "backlog": 0,
    "completed": 0,
    "aborted": 0,
    "completed_percentage": 0,
    "total": 0,
    "weekly_backlog_count": 0,
}


DYNAMIC_STATISTICS = {
    "critical_ports": 0,
    "expiring_rates": 0,
    "cancelled_shipments": 0,
    "live_booking": 0,
    "rate_request": 0,
    "rate_feedback":0,
}


def get_lcl_freight_rate_job_stats(filters={}):
    query = get_query()
    statistics = STATISTICS.copy()
    dynamic_statistics = DYNAMIC_STATISTICS.copy()

    if type(filters) != dict:
        filters = json.loads(filters)

    query = apply_filters(query, filters)
    # getting daily_stats
    if filters.get("daily_stats"):
        statistics = build_daily_details(query, statistics)

    # getting weekly_stats
    if filters.get("weekly_stats"):
        statistics = build_weekly_details(query, statistics)

    # remaining filters
    dynamic_statistics = get_statistics(filters, dynamic_statistics)

    statistics["backlog"] = get_all_backlogs(filters)
    return {
        "dynamic_statistics": dynamic_statistics,
        "statistics": statistics,
    }


def get_query():
    query = LclFreightRateJob.select(LclFreightRateJob.id)
    return query


def apply_indirect_filters(query, filters):
    for key in filters:
        apply_filter_function = f"apply_{key}_filter"
        query = eval(f"{apply_filter_function}(query, filters)")
    return query


def apply_updated_at_filter(query, filters):
    query = query.where(LclFreightRateJob.updated_at > filters["updated_at"])
    return query


def apply_source_filter(query, filters):
    query = query.where(LclFreightRateJob.sources.contains(filters["source"]))
    return query


def apply_start_date_filter(query, filters):
    start_date = filters.get("start_date")
    if start_date:
        start_date = datetime.strptime(start_date, STRING_FORMAT) + timedelta(
            hours=5, minutes=30
        )
        query = query.where(
            LclFreightRateJob.created_at.cast("date") >= start_date.date()
        )
    return query


def apply_end_date_filter(query, filters):
    end_date = filters.get("end_date")
    if end_date:
        end_date = datetime.strptime(end_date, STRING_FORMAT) + timedelta(
            hours=5, minutes=30
        )
        query = query.where(
            LclFreightRateJob.created_at.cast("date") <= end_date.date()
        )
    return query


def get_statistics(filters, dynamic_statistics):
    subquery = LclFreightRateJob.select(
        fn.UNNEST(LclFreightRateJob.sources).alias("element")
    ).alias("elements")
    subquery = apply_filters(subquery, filters)
    subquery = apply_extra_filters(subquery, filters)
    stats_query = (
        LclFreightRateJob.select(
            subquery.c.element, fn.COUNT(subquery.c.element).alias("count")
        )
        .from_(subquery)
        .group_by(subquery.c.element)
        .order_by(fn.COUNT(subquery.c.element).desc())
    )
    data = list(stats_query.dicts())
    for stats in data:
        dynamic_statistics[stats["element"]] = stats["count"]

    return dynamic_statistics


def build_daily_details(query, statistics):
    query = query.where(
        LclFreightRateJob.created_at.cast("date") == datetime.now().date()
    )
    daily_stats_query = query.select(
        LclFreightRateJob.status, fn.COUNT(LclFreightRateJob.id).alias("count")
    ).group_by(LclFreightRateJob.status)

    total_daily_count = 0
    daily_results = json_encoder(list(daily_stats_query.dicts()))
    for data in daily_results:
        total_daily_count += data["count"]
        statistics[data["status"]] = data["count"]
    statistics["completed"] = statistics["completed"] + statistics["aborted"]
    statistics["total"] = total_daily_count
    if total_daily_count != 0:
        statistics["completed_percentage"] = round(
            ((statistics["completed"]) / total_daily_count) * 100, 2
        )
    return statistics


def build_weekly_details(query, statistics):
    query = query.where(
        LclFreightRateJob.created_at.cast("date")
        >= datetime.now().date() - timedelta(days=6)
    )

    weekly_stats_query = query.select(
        LclFreightRateJob.status,
        fn.COUNT(LclFreightRateJob.id).alias("count"),
        LclFreightRateJob.created_at.cast("date").alias("created_at"),
    ).group_by(LclFreightRateJob.status, LclFreightRateJob.created_at.cast("date"))
    weekly_stats_query = weekly_stats_query.order_by(SQL("created_at DESC"))
    weekly_results = json_encoder(list(weekly_stats_query.dicts()))
    weekly_stats = {}

    total_dict = {}
    total_weekly_backlog_count = 0

    for item in weekly_results:
        created_at = item["created_at"]
        status = item["status"]
        count = item["count"]

        if created_at not in total_dict:
            total_dict[created_at] = {
                "pending": 0,
                "completed": 0,
                "backlog": 0,
                "aborted": 0,
            }

        if status == "backlog":
            total_weekly_backlog_count += count

        total_dict[created_at][status] = count

    for date in total_dict:
        total_task_per_day = (
            total_dict[date]["pending"]
            + total_dict[date]["completed"]
            + total_dict[date]["backlog"]
            + total_dict[date]["aborted"]
        )
        total_completed_per_day = (
            total_dict[date]["completed"] + total_dict[date]["aborted"]
        )
        if total_task_per_day != 0:
            weekly_stats[date] = round(
                (total_completed_per_day / total_task_per_day * 100), 2
            )

    statistics["weekly_completed_percentage"] = weekly_stats

    statistics["weekly_backlog_count"] = total_weekly_backlog_count
    return statistics


def apply_filters(query, filters):
    direct_filters, indirect_filters = get_applicable_filters(
        filters, possible_direct_filters, possible_indirect_filters
    )
    # applying direct filters
    query = get_filters(direct_filters, query, LclFreightRateJob)

    # applying indirect filters
    query = apply_indirect_filters(query, indirect_filters)
    
    query = apply_is_visible_filter(query)

    return query


def apply_extra_filters(query, filters):
    applicable_filters = {}
    for key in uncommon_filters:
        if filters.get(key):
            applicable_filters[key] = filters[key]

    query = get_filters(applicable_filters, query, LclFreightRateJob)
    query = apply_start_date_filter(query, filters)
    query = apply_end_date_filter(query, filters)
    return query


def get_all_backlogs(filters):
    query = LclFreightRateJob.select()
    if filters.get("user_id"):
        query = query.where(LclFreightRateJob.user_id == filters.get("user_id"))
    backlog_count = query.where(LclFreightRateJob.status == "backlog").count()

    return backlog_count

def apply_is_visible_filter(query):
    query = query.where(LclFreightRateJob.is_visible == True)
    return query
