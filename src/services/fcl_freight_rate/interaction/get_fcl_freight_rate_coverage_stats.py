from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJobs
import json
from libs.get_applicable_filters import get_applicable_filters
from libs.get_filters import get_filters
from libs.json_encoder import json_encoder
from datetime import datetime, timedelta
import time
from peewee import fn

possible_direct_filters = ['origin_port_id','destination_port_id','shipping_line_id','commodity']
possible_indirect_filters = ['date_range', 'user_id']

STRING_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

STATISTICS = {
            'pending': 0,
            'backlog': 0,
            'completed': 0,
            'completed_percentage':0,
            'total' : 0,
            'weekly_backlog_count' : 0
        }

def get_fcl_freight_rate_coverage_stats(filters = {}):
        statistics = STATISTICS.copy()
        ## Query to get Daily Stats
        daily_query = get_daily_query()
        ## Query to get Weekly Detials
        weekly_query = get_weekly_query()

        if filters:
                if type(filters) != dict:
                        filters = json.loads(filters)

                # GET FILTERS
                direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)

                # APPLY DIRECT FILTERS for Daily and Weekly
                daily_query = get_filters(direct_filters, daily_query, FclFreightRateJobs)
                weekly_query = get_filters(direct_filters, weekly_query, FclFreightRateJobs)

                # APPLY INDIRECT FILTERS for Daily and Weekly
                daily_query = apply_indirect_filters(daily_query, indirect_filters)
                weekly_query = apply_indirect_filters(weekly_query, indirect_filters)

        daily_statistics = build_daily_details(daily_query)
        weekly_statistics = build_weekly_details(weekly_query)

        return daily_statistics,weekly_statistics


# TODAY'S TASKS
# a. Whatever Jobs created today
# b. Whatever Jobs that is still active
def get_daily_query():
    stats = FclFreightRateJobs.select(
         FclFreightRateJobs.status,
         FclFreightRateJobs.origin_port_id,
         FclFreightRateJobs.destination_port_id,
         FclFreightRateJobs.shipping_line_id,
         FclFreightRateJobs.commodity,
         FclFreightRateJobs.assigned_to_id
         ).where(
              FclFreightRateJobs.created_at.cast('date') == datetime.now().date()
        )
    return stats

# WEEKLY DETAILS : Whatever Jobs created in past 7 days
def get_weekly_query():
    query = FclFreightRateJobs.select(
         FclFreightRateJobs.status,
         FclFreightRateJobs.origin_port_id,
         FclFreightRateJobs.destination_port_id,
         FclFreightRateJobs.shipping_line_id,
         FclFreightRateJobs.commodity,
         FclFreightRateJobs.assigned_to_id
    ).where(
            FclFreightRateJobs.created_at.cast('date') >= datetime.now().date()-timedelta(days=7)
    )
    return query

def build_daily_details(query):
    daily_stats_query = query.select(
          FclFreightRateJobs.status,
          fn.COUNT(FclFreightRateJobs.id).alias('count')
     ).group_by(
          FclFreightRateJobs.status
    )

    daily_stats = {}
    daily_results = json_encoder(list(daily_stats_query.dicts()))
    for data in daily_results:
        daily_stats[data['status']] = data['count']

    return daily_stats

def build_weekly_details(query):
    weekly_stats_query = query.select(
          FclFreightRateJobs.status,
          fn.COUNT(FclFreightRateJobs.id).alias('count'),
          FclFreightRateJobs.created_at.cast('date')
     ).group_by(
          FclFreightRateJobs.status,
          FclFreightRateJobs.created_at.cast('date')
    )
    weekly_results = json_encoder(list(weekly_stats_query.dicts()))
    weekly_stats = {}

    total_dict = {}
    total_weekly_backlog_count = 0

    for item in weekly_results:
        created_at = item['created_at']
        status = item['status']
        count = item['count']

        if created_at not in total_dict:
            total_dict[created_at] = {
                      'pending':0,
                      'completed':0,
                      'backlog':0,
                      'aborted':0
                 }

        if status == 'backlog':
            total_weekly_backlog_count += count

        total_dict[created_at][status] = count

    for date in total_dict:
        total_task_per_day = total_dict[date]['pending'] + total_dict[date]['completed'] + total_dict[date]['backlog'] + total_dict[date]['aborted']
        total_completed_per_day = total_dict[date]['completed']
        weekly_stats[date] = round((total_completed_per_day/total_task_per_day * 100))

    weekly_stats['total_weekly_backlog_count'] = total_weekly_backlog_count
    return weekly_stats

def apply_indirect_filters(query, filters):
    for key in filters:
        apply_filter_function = f'apply_{key}_filter'
        query = eval(f'{apply_filter_function}(query, filters)')
    return query

def apply_date_range_filter(query, filters):
    query = query.where(
         FclFreightRateJobs.created_at.cast('date') >= filters['date_range']['startDate'],
         FclFreightRateJobs.created_at.cast('date') <= filters['date_range']['endDate'],
         )
    return query

def apply_user_id_filter(query, filters):
     query = query.where(FclFreightRateJobs.assigned_to_id == filters['user_id'])
     return query
