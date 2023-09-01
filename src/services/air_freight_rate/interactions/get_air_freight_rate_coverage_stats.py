from services.air_freight_rate.models.air_freight_rate_jobs import AirFreightRateJobs
import json
from datetime import datetime, timedelta
from libs.json_encoder import json_encoder
from libs.get_applicable_filters import get_applicable_filters
from libs.get_filters import get_filters
from collections import Counter

possible_direct_filters = ['origin_airport_id','destination_airport_id','airline_id','commodity','status']
possible_indirect_filters = ['date_range', 'user_id']

STRING_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

STATISTICS = {
            'pending': 0,
            'backlog': 0,
            'completed': 0,
            'completed_percentage':0,
            'spot_search' : 0,
            'critical_ports' : 0,
            'expiring_rates' : 0,
            'monitoring_dashboard' : 0,
            'cancelled_shipments' : 0,
            'total' : 0,
            'weekly_backlog_count' : 0
        }

def get_air_freight_rate_coverage_stats(filters = {}, page_limit = 10, page = 1, sort_by = 'created_at', sort_type = 'desc'):
    daily_query = get_daily_query(sort_by, sort_type)
    weekly_query = get_weekly_query(sort_by, sort_type)

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)

        daily_query = get_filters(direct_filters, daily_query, AirFreightRateJobs)
        weekly_query = get_filters(direct_filters, weekly_query, AirFreightRateJobs)

        daily_query = apply_indirect_filters(daily_query, indirect_filters)
        weekly_query = apply_indirect_filters(weekly_query, indirect_filters)
  
    statistics = STATISTICS.copy()
    statistics = statistics if not daily_query else get_daily_stats_data(daily_query, statistics)
    statistics = statistics if not weekly_query else get_weekly_details(weekly_query, statistics)
    
    return statistics

def get_daily_query(sort_by, sort_type):
  query = AirFreightRateJobs.select().where(
       (AirFreightRateJobs.created_at > datetime.now()-timedelta(days=1))|
       (AirFreightRateJobs.status == 'active')
    )
  if sort_by:
      query = query.order_by(eval('AirFreightRateJobs.{}.{}()'.format(sort_by,sort_type)))
  return query

def get_weekly_query(sort_by, sort_type):
  query = AirFreightRateJobs.select().where(
      AirFreightRateJobs.created_at > datetime.now()-timedelta(days=7)
    )
  if sort_by:
    query = query.order_by(eval('AirFreightRateJobs.{}.{}()'.format(sort_by,sort_type)))
  return query

def get_daily_stats_data(query,statistics):
    raw_data = json_encoder(list(query.dicts()))
    statistics['total'] = len(raw_data)
    for item in raw_data:
      status = item['status']
      created_at = item['created_at']

      if status == 'active':
        if datetime.strptime(created_at,STRING_FORMAT) > datetime.now()-timedelta(days=1):
          statistics['pending'] += 1
        else:
          statistics['backlog'] += 1
      else:
        if datetime.strptime(created_at,STRING_FORMAT) > datetime.now()-timedelta(days=1):
          statistics['completed'] += 1

      source = item['source']
      if source in statistics:
          statistics[source] += 1
           
    if statistics['total']:
      statistics['completed_percentage'] = round((statistics['completed']/statistics['total'])*100)

    return statistics

def get_weekly_details(query,statistics):
    raw_data = json_encoder(list(query.dicts()))
    total_weekly_backlog = 0

    current_date = datetime.now().date()

    weekly_completed_percentage = {}
    task_counts = {}
    backlog_counts = {}
    start_date = current_date - timedelta(days=6)

    for day_offset in range(6):
        date = start_date + timedelta(days=day_offset)
        weekly_completed_percentage[date] = 0

    for task in raw_data:
         created_at = datetime.strptime(task['created_at'], STRING_FORMAT)
         if start_date <= created_at.date() <= current_date:
                if created_at.date() not in task_counts:
                    backlog_counts[created_at.date()] = 0
                    task_counts[created_at.date()] = 0

                task_counts[created_at.date()] +=1

                if task['status'] == 'active':
                     backlog_counts[created_at.date()] +=1

    for day, count in task_counts.items():
         backlog = backlog_counts[day]
         total_weekly_backlog += backlog

         if count:
              weekly_completed_percentage[day] = round((1 - (backlog/count))*100)

    statistics['weekly_backlog_count'] = total_weekly_backlog
    statistics['weekly_completed_percentage'] = weekly_completed_percentage

    return statistics

def apply_indirect_filters(query, filters):
  for key in filters:
    apply_filter_function = f'apply_{key}_filter'
    query = eval(f'{apply_filter_function}(query, filters)')
  return query
