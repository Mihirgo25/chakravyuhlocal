from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJobs
from services.fcl_freight_rate.helpers.generate_csv_file_url_for_fcl import (
    generate_csv_file_url_for_fcl,
)
import json
from libs.get_applicable_filters import get_applicable_filters
from libs.get_filters import get_filters
from libs.json_encoder import json_encoder
from datetime import datetime, timedelta
from peewee import fn
from playhouse.postgres_ext import SQL


STRING_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"

possible_direct_filters = [
    "origin_port_id",
    "destination_port_id",
    "shipping_line_id",
    "commodity",
    "status",
    "serial_id",
]
possible_indirect_filters = ["source", "updated_at", "user_id", "date_range"]

DEFAULT_REQUIRED_FIELDS = [
    "id",
    "assigned_to",
    "closed_by",
    "closed_by_id",
    "closing_remarks",
    "commodity",
    "container_size",
    "created_at",
    "updated_at",
    "status",
    "shipping_line",
    "shipping_line_id",
    "service_provider",
    "service_provider_id",
    "origin_port",
    "origin_port_id",
    "destination_port",
    "destination_port_id",
    "serial_id",
    "container_type",
]

STATISTICS = {
    "pending": 0,
    "backlog": 0,
    "completed": 0,
    "aborted": 0,
    "completed_percentage": 0,
    "total": 0,
    "weekly_backlog_count": 0,
}


def list_fcl_freight_rate_jobs(
    filters={},
    page_limit=10,
    page=1,
    sort_by="updated_at",
    sort_type="desc",
    generate_csv_url=False,
    includes={},
):
    query = includes_filter(includes)
    statistics = STATISTICS.copy()
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)
        direct_filters, indirect_filters = get_applicable_filters(
            filters, possible_direct_filters, possible_indirect_filters
        )
        query = get_filters(direct_filters, query, FclFreightRateJobs)
        query = apply_indirect_filters(query, indirect_filters)
        if filters.get("daily_stats"):
            statistics = build_daily_details(query, statistics)

        if filters.get("weekly_stats"):
            statistics = build_weekly_details(query, statistics)

        dynamic_statisitcs = get_statisitcs(query)

    if generate_csv_url:
        return generate_csv_file_url_for_fcl(query)

    if page_limit:
        query = query.paginate(page, page_limit)

    query = sort_query(sort_by, sort_type, query)

    data = get_data(query)

    return {"list": data, "stats": dynamic_statisitcs}


def build_daily_details(query, statistics):
    query = query.where(
        FclFreightRateJobs.created_at.cast("date") == datetime.now().date()
    )

    daily_stats_query = query.select(
        FclFreightRateJobs.status, fn.COUNT(FclFreightRateJobs.id).alias("count")
    ).group_by(FclFreightRateJobs.status)

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
        FclFreightRateJobs.created_at.cast("date")
        >= datetime.now().date() - timedelta(days=7)
    )

    weekly_stats_query = query.select(
        FclFreightRateJobs.status,
        fn.COUNT(FclFreightRateJobs.id).alias("count"),
        FclFreightRateJobs.created_at.cast("date").alias("created_at"),
    ).group_by(FclFreightRateJobs.status, FclFreightRateJobs.created_at.cast("date"))
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


def get_statisitcs(query):
    dynamic_statisitcs = {}
    return dynamic_statisitcs


def get_data(query):
    return list(query.dicts())


def includes_filter(includes):
    if includes:
        fcl_all_fields = list(FclFreightRateJobs._meta.fields.keys())
        required_fcl_fields = [a for a in includes.keys() if a in fcl_all_fields]
        fcl_fields = [getattr(FclFreightRateJobs, key) for key in required_fcl_fields]
    else:
        fcl_fields = [
            getattr(FclFreightRateJobs, key) for key in DEFAULT_REQUIRED_FIELDS
        ]
    query = FclFreightRateJobs.select(*fcl_fields)
    return query


def sort_query(sort_by, sort_type):
    if sort_by:
        query = query.order_by(
            eval("FclFreightRateJobs.{}.{}()".format(sort_by, sort_type))
        )
    return query


def apply_indirect_filters(query, filters):
    for key in filters:
        apply_filter_function = f"apply_{key}_filter"
        query = eval(f"{apply_filter_function}(query, filters)")
    return query


def apply_user_id_filter(query, filters):
    query = query.where(FclFreightRateJobs.assigned_to_id == filters["user_id"])
    return query


def apply_updated_at_filter(query, filters):
    query = query.where(FclFreightRateJobs.updated_at > filters["updated_at"])
    return query


def apply_date_range_filter(query, filters):
    if not filters["date_range"]["startDate"]:
        start_date = datetime.now() - timedelta(days=7)
    else:
        start_date = datetime.strptime(
            filters["date_range"]["startDate"], STRING_FORMAT
        ) + timedelta(hours=5, minutes=30)
    if not filters["date_range"]["endDate"]:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(
            filters["date_range"]["endDate"], STRING_FORMAT
        ) + timedelta(hours=5, minutes=30)
    query = query.where(
        FclFreightRateJobs.created_at.cast("date") >= start_date.date(),
        FclFreightRateJobs.created_at.cast("date") <= end_date.date(),
    )
    return query


def apply_source_filter(query, filters):
    query = query.where(FclFreightRateJobs.sources.contains(filters["source"]))
    return query
