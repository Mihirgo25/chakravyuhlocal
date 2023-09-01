from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJobs
import json
from libs.get_applicable_filters import get_applicable_filters
from libs.get_filters import get_filters
from libs.json_encoder import json_encoder
from datetime import datetime, timedelta

possible_direct_filters = ['origin_port_id','destination_port_id','shipping_line_id','commodity']
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

def get_fcl_freight_rate_coverage_stats(filters = {}, page_limit = 10, page = 1, sort_by = 'created_at', sort_type = 'desc'):
        statistics = STATISTICS.copy()
        ## Query to get Daily Stats
        daily_query = get_daily_query(sort_by, sort_type)
        ## Query to get Weekly Detials
        weekly_query = get_weekly_query(sort_by, sort_type)

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


        # IF NO DATA PRESENT IN DB, return default
        # ELSE, calculate statistics (Daily and Weekly)
        statistics = statistics if not daily_query else get_daily_stats_data(daily_query,statistics)
        statistics = statistics if not weekly_query else get_weekly_details(weekly_query,statistics)

        return statistics


# TODAY'S TASKS
# a. Whatever Jobs created today
# b. Whatever Jobs that is still active
def get_daily_query(sort_by, sort_type):
    query = FclFreightRateJobs.select().where(
             (FclFreightRateJobs.created_at > datetime.now()-timedelta(days=1)) | (FclFreightRateJobs.status == 'active')
        )
    if sort_by:
            query = query.order_by(eval('FclFreightRateJobs.{}.{}()'.format(sort_by,sort_type)))
    return query

# WEEKLY DETAILS : Whatever Jobs created in past 7 days
def get_weekly_query(sort_by, sort_type):
    query = FclFreightRateJobs.select().where(
            FclFreightRateJobs.created_at > datetime.now()-timedelta(days=7)
        )
    if sort_by:
        query = query.order_by(eval('FclFreightRateJobs.{}.{}()'.format(sort_by,sort_type)))
    return query


# a. PENDING: CREATED AT = today and STATUS = active
# b. COMPLETED: CREATED AT = today and STATUS = inactive
# c. BACKLOG: CREATED AT before today and STATUS = active
def get_daily_stats_data(query,statistics):
        raw_data = json_encoder(list(query.dicts()))
        statistics['total'] = len(raw_data)
        for item in raw_data:
            status = item['status']
            created_at = item['created_at']

            if status == 'active':
                if datetime.strptime(created_at,STRING_FORMAT).date() > datetime.now().date()-timedelta(days=1):
                    statistics['pending'] += 1
                else:
                    statistics['backlog'] += 1
            else:
                if datetime.strptime(created_at,STRING_FORMAT).date() > datetime.now().date()-timedelta(days=1):
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

    # Loop through weekly data, find number of jobs created on each day, count jobs that are still active
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

def apply_date_range_filter(query, filters):
    query = query.where(
         FclFreightRateJobs.created_at.cast('date') >= filters['date_range']['startDate'],
         FclFreightRateJobs.created_at.cast('date') <= filters['date_range']['endDate'],
         )
    return query

def apply_user_id_filter(query, filters):
     query = query.where(FclFreightRateJobs.assigned_to_id == filters['user_id'])
     return query
