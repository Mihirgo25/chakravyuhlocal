from services.air_freight_rate.models.air_freight_rate_jobs import AirFreightRateJobs
from services.air_freight_rate.helpers.generate_csv_file_url_for_air import (
    generate_csv_file_url_for_air,
)
import json
from libs.get_applicable_filters import get_applicable_filters
from libs.get_filters import get_filters
from libs.json_encoder import json_encoder
from datetime import datetime, timedelta
from peewee import fn
from playhouse.postgres_ext import SQL, Case


STRING_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"

possible_direct_filters = [
    "origin_airport_id",
    "destination_airport_id",
    "airline_id",
    "commodity",
]
possible_indirect_filters = ["updated_at", "user_id", "start_date", "end_date"]

uncommon_filters = ['serial_id', 'status']

DEFAULT_REQUIRED_FIELDS = [
    "id",
    "assigned_to",
    "closed_by",
    "closing_remarks",
    "commodity",
    "created_at",
    "updated_at",
    "status",
    "airline",
    "airline_id",
    "service_provider",
    "service_provider_id",
    "origin_airport",
    "origin_airport_id",
    "destination_airport",
    "destination_airport_id",
    "shipment_type",
    "stacking_type",
    "commodity_type",
    "commodity_sub_type",
    "operation_type",
    "stacking_type",
    "serial_id",
    "price_type",
]
STRING_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

STATISTICS = {
    "pending": 0,
    "backlog": 0,
    "completed": 0,
    "aborted": 0,
    "completed_percentage": 0,
    "total": 0,
    "weekly_backlog_count": 0,
}


def list_air_freight_rate_jobs(
    filters={},
    page_limit=10,
    page=1,
    sort_by="updated_at",
    sort_type="desc",
    generate_csv_url=False,
    includes={},
):
    query = includes_filters(includes)
    statisitcs = STATISTICS.copy()
    dynamic_statisitcs = {}

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        direct_filters, indirect_filters = get_applicable_filters(
            filters, possible_direct_filters, possible_indirect_filters
        )
        #applying direct filters
        query = get_filters(direct_filters, query, AirFreightRateJobs)

        #applying indirect filters
        query = apply_indirect_filters(query, indirect_filters)

        #getting daily_stats
        if filters.get("daily_stats"):
            statisitcs = build_daily_details(query, statisitcs)

        #getting weekly_stats
        if filters.get("weekly_stats"):
            statisitcs = build_weekly_details(query, statisitcs)
        
        #remaining filters
        if filters.get("source"):
            dynamic_statisitcs = get_statisitcs(query, filters)


    if generate_csv_url:
        return generate_csv_file_url_for_air(query)

    if page_limit:
        query = query.paginate(page, page_limit)

    query = sort_query(sort_by, sort_type, query)

    data = get_data(query)

    return {
        "list": data,
        "dynamic_statisitcs": dynamic_statisitcs,
        "statisitcs": statisitcs,
    }

def get_data(query):
    return list(query.dicts())


def includes_filters(includes):
    if includes:
        fcl_all_fields = list(AirFreightRateJobs._meta.fields.keys())
        required_fcl_fields = [a for a in includes.keys() if a in fcl_all_fields]
        air_fields = [getattr(AirFreightRateJobs, key) for key in required_fcl_fields]
    else:
        air_fields = [
            getattr(AirFreightRateJobs, key) for key in DEFAULT_REQUIRED_FIELDS
        ]
    query = AirFreightRateJobs.select(*air_fields)
    return query


def sort_query(sort_by, sort_type, query):
    if sort_by:
        query = query.order_by(
            eval("AirFreightRateJobs.{}.{}()".format(sort_by, sort_type))
        )
    return query


def apply_indirect_filters(query, filters):
    for key in filters:
        apply_filter_function = f"apply_{key}_filter"
        query = eval(f"{apply_filter_function}(query, filters)")
    return query


def apply_user_id_filter(query, filters):
    query = query.where(AirFreightRateJobs.assigned_to_id == filters["user_id"])
    return query


def apply_updated_at_filter(query, filters):
    query = query.where(AirFreightRateJobs.updated_at > filters["updated_at"])
    return query

def apply_source_filter(query, filters):
    query = query.where(AirFreightRateJobs.sources.contains(filters["source"]))
    return query


def apply_start_date_filter(query, filters):
    query = query.where(
        AirFreightRateJobs.created_at.cast("date") >= filters["start_date"].date()
    )
    return query


def apply_end_date_filter(query, filters):
    query = query.where(
        AirFreightRateJobs.created_at.cast("date") <= filters["end_date"].date()
    )
    return query




def get_statisitcs(query, filters):
    subquery = (AirFreightRateJobs.select(fn.UNNEST(AirFreightRateJobs.sources).alias('element')).alias('elements'))
    stats_query = AirFreightRateJobs.select(subquery.c.element, fn.COUNT(subquery.c.element).alias('count')).from_(subquery).group_by(subquery.c.element).order_by(fn.COUNT(subquery.c.element).desc())
    data = list(stats_query.dicts())
    dynamic_statisitcs = {}
    for stats in data:
        dynamic_statisitcs[stats['element']] = stats['count']
    
    query = apply_source_filter(query, filters)
    applicable_filters ={}
    for key in uncommon_filters:
        if filters.get(key):
            applicable_filters[key] = filters[key]
    query = get_filters(applicable_filters, query, AirFreightRateJobs)
    return dynamic_statisitcs


def build_daily_details(query, statistics):
    query = query.where(
        AirFreightRateJobs.created_at.cast("date") == datetime.now().date()
    )
    daily_stats_query = query.select(
        AirFreightRateJobs.status, fn.COUNT(AirFreightRateJobs.id).alias("count")
    ).group_by(AirFreightRateJobs.status)

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
        AirFreightRateJobs.created_at.cast("date")
        >= datetime.now().date() - timedelta(days=7)
    )
    weekly_stats_query = query.select(
        AirFreightRateJobs.status,
        fn.COUNT(AirFreightRateJobs.id).alias("count"),
        AirFreightRateJobs.created_at.cast("date").alias("created_at"),
    ).group_by(AirFreightRateJobs.status, AirFreightRateJobs.created_at.cast("date"))
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

