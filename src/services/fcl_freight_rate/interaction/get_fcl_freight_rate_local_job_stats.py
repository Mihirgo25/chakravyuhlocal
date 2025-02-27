from services.fcl_freight_rate.models.fcl_freight_rate_local_job import FclFreightRateLocalJob
from services.fcl_freight_rate.models.fcl_freight_rate_local_job_mapping import (
    FclFreightRateLocalJobMapping,
)
import json
from functools import reduce
from libs.get_applicable_filters import get_applicable_filters
from libs.get_filters import get_filters
from libs.json_encoder import json_encoder
from datetime import datetime, timedelta
from peewee import fn
from playhouse.postgres_ext import SQL


possible_direct_filters = [
    "port_id",
    "shipping_line_id",
    "commodity",
    "user_id",
    "cogo_entity_id",
    "service_provider_id",
]
possible_indirect_filters = ["updated_at", "is_flash_booking_reverted", "source_id", "source_serial_id"]

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



def get_fcl_freight_rate_local_job_stats(
    filters={}
):
    query = get_query()
    statistics = STATISTICS.copy()
    dynamic_statistics = DYNAMIC_STATISTICS.copy()

    if type(filters) != dict:
        filters = json.loads(filters)

    query = apply_filters(query, filters)
    # getting daily_stats
    if filters.get("daily_stats"):
        statistics = build_daily_details(query, statistics, filters)

    # getting weekly_stats
    if filters.get("weekly_stats"):
        statistics = build_weekly_details(query, statistics, filters)

    # remaining filters
    dynamic_statistics = get_statistics(
            filters, dynamic_statistics
        )
    
    statistics['backlog'] = get_all_backlogs(filters)
    return {
        "dynamic_statistics": dynamic_statistics,
        "statistics": statistics,
    }



def get_query():
    query = FclFreightRateLocalJob.select(FclFreightRateLocalJob.id)
    return query


def apply_indirect_filters(query, filters):
    for key in filters:
        apply_filter_function = f"apply_{key}_filter"
        query = eval(f"{apply_filter_function}(query, filters)")
    return query


def apply_updated_at_filter(query, filters):
    query = query.where(FclFreightRateLocalJob.updated_at > filters["updated_at"])
    return query


def apply_source_filter(query, filters):
    if filters.get('source'):
        if not isinstance(filters.get('source'), list):
            filters['source'] = [filters.get('source')]
        conditions = [FclFreightRateLocalJob.sources.contains(tag) for tag in filters["source"]]
        combined_condition = reduce(lambda a, b: a | b, conditions)
        query = query.where(combined_condition)
    return query


def apply_start_date_filter(query, filters):
    start_date = filters.get("start_date")
    if start_date:
        start_date = datetime.strptime(start_date, STRING_FORMAT) + timedelta(
            hours=5, minutes=30
        )
        query = query.where(FclFreightRateLocalJob.updated_at.cast("date") >= start_date.date())
    return query


def apply_end_date_filter(query, filters):
    end_date = filters.get("end_date")
    if end_date:
        end_date = datetime.strptime(end_date, STRING_FORMAT) + timedelta(
            hours=5, minutes=30
        )
        query = query.where(FclFreightRateLocalJob.updated_at.cast("date") <= end_date.date())
    return query


def get_statistics(filters, dynamic_statistics):
    subquery = FclFreightRateLocalJob.select(
        fn.UNNEST(FclFreightRateLocalJob.sources).alias("element")
    ).alias("elements")
    subquery = apply_filters(subquery, filters)
    subquery = apply_extra_filters(subquery, filters)
    if (not(filters.get("start_date") or filters.get("end_date"))) and "completed" in filters.get("status"):
        subquery = subquery.where(
            FclFreightRateLocalJob.updated_at.cast("date") == datetime.now().date()
        )
    stats_query = (
        FclFreightRateLocalJob.select(
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


def build_daily_details(query, statistics, filters):
    
    query, pending_count = apply_date_filter_and_get_pending_count(query, filters)
    statistics['pending'] = pending_count
    
    query = query.select(
        FclFreightRateLocalJob.status, fn.COUNT(FclFreightRateLocalJob.id).alias("count")
    ).where(FclFreightRateLocalJob.status.not_in(['skipped', 'pending'])).group_by(FclFreightRateLocalJob.status)

    total_daily_count = 0
    total_completed = 0
    daily_results = json_encoder(list(query.dicts()))
    for data in daily_results:
        total_daily_count += data["count"]
        if data['status'] in ["completed", "aborted"]:
            total_completed += data["count"]
    
    statistics['completed'] = total_completed
    statistics["total"] = total_daily_count + pending_count
    
    if statistics["total"] != 0:
        statistics["completed_percentage"] = round(
            (total_completed / statistics["total"] ) * 100, 2
        )
    else:
        statistics["completed_percentage"] = 100
        
    return statistics

def apply_date_filter_and_get_pending_count(query, filters):
    
    query = apply_start_date_filter(query, filters)
    query = apply_end_date_filter(query, filters)

    pending_count = query.where(FclFreightRateLocalJob.status == 'pending').count()
    
    if not(filters.get("start_date") or filters.get("end_date")):
        query = query.where(
            FclFreightRateLocalJob.updated_at.cast("date") == datetime.now().date()
        )
        
    return query, pending_count


def build_weekly_details(query, statistics, filters):
    query = query.where(
        FclFreightRateLocalJob.created_at.cast("date")
        >= datetime.now().date() - timedelta(days=6)
    )
    
    query = apply_source_filter(query, filters)
    weekly_stats_query = query.select(
        FclFreightRateLocalJob.status,
        fn.COUNT(FclFreightRateLocalJob.id).alias("count"),
        FclFreightRateLocalJob.created_at.cast("date").alias("created_at"),
    ).group_by(FclFreightRateLocalJob.status, FclFreightRateLocalJob.created_at.cast("date"))
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
        else: 
            weekly_stats[date] = 100

    statistics["weekly_completed_percentage"] = weekly_stats

    statistics["weekly_backlog_count"] = total_weekly_backlog_count
    return statistics


def apply_filters(query, filters):
    direct_filters, indirect_filters = get_applicable_filters(
        filters, possible_direct_filters, possible_indirect_filters
    )
    # applying direct filters
    query = get_filters(direct_filters, query, FclFreightRateLocalJob)

    # applying indirect filters
    query = apply_indirect_filters(query, indirect_filters)
    
    query = apply_is_visible_filter(query)

    return query


def apply_extra_filters(query, filters):
    applicable_filters = {}
    for key in uncommon_filters:
        if filters.get(key):
            applicable_filters[key] = filters[key]

    query = get_filters(applicable_filters, query, FclFreightRateLocalJob)
    query = apply_start_date_filter(query, filters)
    query = apply_end_date_filter(query, filters)
    return query

def get_all_backlogs(filters):
    query = FclFreightRateLocalJob.select()
    if filters.get('user_id'):
        query = query.where(FclFreightRateLocalJob.user_id == filters.get('user_id'))
    backlog_count = query.where(FclFreightRateLocalJob.status == 'backlog').count()

    return backlog_count

def apply_source_id_filter(query, filters):
    if filters.get('source_id') and not isinstance(filters.get('source_id'), list):
        filters['source_id'] = [filters.get('source_id')]
    subquery = list(FclFreightRateLocalJobMapping.select(FclFreightRateLocalJobMapping.job_id).where(FclFreightRateLocalJobMapping.source_id << filters['source_id']).dicts())
    job_ids = []
    for data in subquery:
        job_ids.append(data['job_id'])
    query = query.where(FclFreightRateLocalJob.id << job_ids)
    return query

def apply_source_serial_id_filter(query, filters):
    if filters.get('source_serial_id') and not isinstance(filters.get('source_serial_id'), list):
        filters['source_serial_id'] = [filters.get('source_serial_id')]
    subquery = list(FclFreightRateLocalJobMapping.select(FclFreightRateLocalJobMapping.job_id).where(FclFreightRateLocalJobMapping.source_serial_id << filters['source_serial_id']).dicts())
    job_ids = []
    for data in subquery:
        job_ids.append(data['job_id'])
    query = query.where(FclFreightRateLocalJob.id << job_ids)
    return query

def apply_is_flash_booking_reverted_filter(query, filters):
    if filters.get('is_flash_booking_reverted'):
        query = query.join(FclFreightRateLocalJobMapping, on=(FclFreightRateLocalJobMapping.job_id == FclFreightRateLocalJob.id)).where(FclFreightRateLocalJobMapping.status == 'reverted')
    else:
        query = query.join(FclFreightRateLocalJobMapping, on=(FclFreightRateLocalJobMapping.job_id == FclFreightRateLocalJob.id)).where(FclFreightRateLocalJobMapping.status != 'reverted')
    return query

def apply_is_visible_filter(query):
    query = query.where(FclFreightRateLocalJob.is_visible == True)
    return query