from services.air_freight_rate.models.air_freight_rate_jobs import AirFreightRateJobs
import json
from libs.get_applicable_filters import get_applicable_filters
from libs.get_filters import get_filters
from libs.json_encoder import json_encoder
from datetime import datetime, timedelta
import time
from peewee import fn

possible_direct_filters = ['origin_airport_id','destination_airport_id','airline_id','commodity']
possible_indirect_filters = ['date_range', 'user_id']

STRING_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

STATISTICS = {
            'pending': 0,
            'backlog': 0,
            'completed': 0,
            'aborted':0,
            'completed_percentage':0,
            'total' : 0,
            'weekly_backlog_count' : 0
        }

def get_air_freight_rate_coverage_stats(filters = {}):
        statistics = STATISTICS.copy()
        ## Query to get Daily Stats
        daily_query = get_daily_query(filters)
        ## Query to get Weekly Detials
        weekly_query = get_weekly_query(filters)

        statistics = build_daily_details(daily_query,statistics)
        statistics = build_weekly_details(weekly_query,statistics)

        return statistics

def apply_filters_for_query(query,filters):
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
        query = get_filters(direct_filters, query, AirFreightRateJobs)
        query = apply_indirect_filters(query, indirect_filters)

    return query


def get_daily_query(filters):
    query = AirFreightRateJobs.select(
         AirFreightRateJobs.status,
         AirFreightRateJobs.origin_airport_id,
         AirFreightRateJobs.destination_airport_id,
         AirFreightRateJobs.airline_id,
         AirFreightRateJobs.commodity,
         AirFreightRateJobs.assigned_to_id
         ).where(
              AirFreightRateJobs.created_at.cast('date') == datetime.now().date()
        )

    query = apply_filters_for_query(query,filters)
    return query

def get_weekly_query(filters):
    query = AirFreightRateJobs.select(
         AirFreightRateJobs.status,
         AirFreightRateJobs.origin_airport_id,
         AirFreightRateJobs.destination_airport_id,
         AirFreightRateJobs.airline_id,
         AirFreightRateJobs.commodity,
         AirFreightRateJobs.assigned_to_id
    ).where(
            AirFreightRateJobs.created_at.cast('date') >= datetime.now().date()-timedelta(days=7)
    )
    query = apply_filters_for_query(query,filters)
    return query

def build_daily_details(query,statistics):
    daily_stats_query = query.select(
          AirFreightRateJobs.status,
          fn.COUNT(AirFreightRateJobs.id).alias('count')
     ).group_by(
          AirFreightRateJobs.status
    )

    total_daily_count = 0
    daily_results = json_encoder(list(daily_stats_query.dicts()))
    for data in daily_results:
        total_daily_count += data['count']
        statistics[data['status']] = data['count']

    statistics['total'] = total_daily_count
    if total_daily_count != 0:
        statistics['completed_percentage'] = round(((statistics['completed']+statistics['aborted'])/total_daily_count)*100,2)
    return statistics

def build_weekly_details(query,statistics):
    weekly_stats_query = query.select(
          AirFreightRateJobs.status,
          fn.COUNT(AirFreightRateJobs.id).alias('count'),
          AirFreightRateJobs.created_at.cast('date')
     ).group_by(
          AirFreightRateJobs.status,
          AirFreightRateJobs.created_at.cast('date')
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
        total_completed_per_day = total_dict[date]['completed'] + total_dict[date]['aborted']
        weekly_stats[date] = round((total_completed_per_day/total_task_per_day * 100),2)

    statistics['weekly_completed_percentage'] = weekly_stats

    statistics['weekly_backlog_count'] = total_weekly_backlog_count
    return statistics

def apply_indirect_filters(query, filters):
    for key in filters:
        apply_filter_function = f'apply_{key}_filter'
        query = eval(f'{apply_filter_function}(query, filters)')
    return query

def apply_date_range_filter(query, filters):
    query = query.where(
         AirFreightRateJobs.created_at.cast('date') >= filters['date_range']['startDate'],
         AirFreightRateJobs.created_at.cast('date') <= filters['date_range']['endDate'],
         )
    return query

def apply_user_id_filter(query, filters):
     query = query.where(AirFreightRateJobs.assigned_to_id == filters['user_id'])
     return query
