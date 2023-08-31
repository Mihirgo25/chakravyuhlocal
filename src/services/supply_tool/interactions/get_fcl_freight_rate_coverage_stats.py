from services.supply_tool.models.fcl_freight_rate_jobs import FclFreightRateJobs
import json
from libs.get_applicable_filters import get_applicable_filters
from libs.get_filters import get_filters
from libs.json_encoder import json_encoder
from datetime import datetime, timedelta
from collections import Counter

possible_direct_filters = ['origin_port_id','destination_port_id','shipping_line_id','commodity','status']
possible_indirect_filters = ['updated_at', 'user_id']

def get_fcl_freight_rate_coverage_stats(filters = {}, page_limit = 10, page = 1, sort_by = 'created_at', sort_type = 'desc'):
    daily_query = get_daily_query(sort_by, sort_type)
    weekly_query = get_weekly_query(sort_by, sort_type)

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)

        daily_query = get_filters(direct_filters, daily_query, FclFreightRateJobs)
        weekly_query = get_filters(direct_filters, weekly_query, FclFreightRateJobs)

        daily_query = apply_indirect_filters(daily_query, indirect_filters)
        weekly_query = apply_indirect_filters(weekly_query, indirect_filters)

    statistics = {
      'pending': 0,
      'backlog': 0,
      'completed': 0,
      'spot_search' : 0,
      'critical_port_pair' : 0,
      'expiring_rates' : 0,
      'monitoring_dashboard' : 0,
      'cancelled_shipment' : 0,
      'total' : 0,
      'previous_day_0' : 100,
      'previous_day_1' : 100,
      'previous_day_2' : 100,
      'previous_day_3' : 100,
      'previous_day_4' : 100,
      'previous_day_5' : 100,
      'previous_day_6' : 100,
      'weekly_backlog' : 0
    }

    if not daily_query:
       return statistics

    statistics = get_daily_stats_data(daily_query,statistics)

    if not weekly_query:
       return statistics

    statistics = get_weekly_details(weekly_query, statistics)

    return statistics


def get_daily_query(sort_by, sort_type):
  query = FclFreightRateJobs.select().where(
       (FclFreightRateJobs.created_at > datetime.now()-timedelta(days=1))
    )
  if sort_by:
      query = query.order_by(eval('FclFreightRateJobs.{}.{}()'.format(sort_by,sort_type)))
  return query

def get_weekly_query(sort_by, sort_type):
  query = FclFreightRateJobs.select().where(
      FclFreightRateJobs.created_at > datetime.now()-timedelta(days=7)
    )
  if sort_by:
    query = query.order_by(eval('FclFreightRateJobs.{}.{}()'.format(sort_by,sort_type)))
  return query


def get_daily_stats_data(query,statistics):
    raw_data = json_encoder(list(query.dicts()))
    statistics['total'] = len(raw_data)
    for item in raw_data:
      status = item['status']
      created_at = item['created_at']

      if status == 'active':
        if datetime.strptime(created_at,"%Y-%m-%dT%H:%M:%S.%fZ") > datetime.now()-timedelta(days=1):
          statistics['pending'] += 1
        else:
          statistics['backlog'] += 1
      else:
        if datetime.strptime(created_at,"%Y-%m-%dT%H:%M:%S.%fZ") > datetime.now()-timedelta(days=1):
          statistics['completed'] += 1

        source = item['source']
        if source in statistics:
           statistics[source] += 1

    return statistics

def get_weekly_details(query, statistics):
  raw_data = json_encoder(list(query.dicts()))
  total_backlog = 0

  current_date = datetime.now().date()

  backlogs_per_day = Counter()
  total_tasks_per_day = Counter()

  start_date = current_date - timedelta(days=7)

  for task in raw_data:
    created_at = datetime.strptime(task['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
    if start_date <= created_at.date() <= current_date:
        days_ago = (current_date - created_at.date()).days
        total_tasks_per_day[days_ago] += 1
        if task['status'] == 'active':
          backlogs_per_day[days_ago] += 1

  for days_ago, count in total_tasks_per_day.items():
    backlog_count = backlogs_per_day[days_ago]
    total_backlog += backlog_count

    if count:
      statistics['previous_day_' + str(days_ago)] = round((1 - (backlog_count/count))*100)

  statistics['weekly_backlog'] = total_backlog

  return statistics

def apply_indirect_filters(query, filters):
  for key in filters:
    apply_filter_function = f'apply_{key}_filter'
    query = eval(f'{apply_filter_function}(query, filters)')
  return query

def apply_updated_at_filter(query, filters):
  query = query.where(FclFreightRateJobs.updated_at > filters['updated_at'])
  return query

def apply_user_id_filter(query, filters):
   query = query.where(FclFreightRateJobs.assigned_to_id == filters['user_id'])
