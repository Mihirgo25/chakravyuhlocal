from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from services.fcl_freight_rate.models.fcl_freight_rate_task import FclFreightRateTask
from datetime import datetime, timedelta
from peewee import fn
from database.rails_db import *

def get_fcl_freight_rate_stats(request):
    response = {}
    for stats_type in request["stats_types"]:
        try:
            response[stats_type] = eval(f"get_{stats_type}_stats({request})")
        except:
            response[stats_type] = None

    return response

def get_tech_ops_dashboard_stats(request):
    tasks = FclFreightRateTask.select(
        FclFreightRateTask.completed_by_id.alias('performed_by_id'),
        fn.COUNT(FclFreightRateTask.id).alias('rates_count'),
        fn.SUM(FclFreightRateTask.source_count).alias('shipments_count'),
        fn.json_agg(fn.json_build_object(
            'created_at', FclFreightRateTask.created_at,
            'completed_at', FclFreightRateTask.completed_at
        )).alias("tats")
        ).where(FclFreightRateTask.status == 'completed').where(
        FclFreightRateTask.completed_at >= datetime.strptime(request['validity_start'],'%Y-%m-%d') and FclFreightRateTask.completed_at <= datetime.strptime(request['validity_end'],'%Y-%m-%d') + timedelta(days = 1)
        ).group_by(FclFreightRateTask.completed_by_id)

    stats = list(tasks.dicts())

    if not stats:
        return stats 

    user_ids = list(set([t['performed_by_id'] for t in stats]))
    users = get_user(user_ids)
    
    users = [{'id':str(user['id']), 'name':user['name'], 'email':user['email'], 'mobile_number_eformat':user['mobile_number_eformat']} for user in users]
    users = {user['id']: user for user in users}

    average_tat = 0

    for stat in stats:
        try:
            stat['performed_by'] = users[stat['performed_by_id']]
        except:
            stat['performed_by'] = None

        average_tat = 0.0
        stat['0-3'] = 0
        stat['4-6'] = 0
        stat['>6'] = 0
        
        for tat in stat['tats']: 
            completion_time = (int(round(datetime.fromisoformat(tat['completed_at']).timestamp())) - int(round(datetime.strptime(tat['created_at'], '%Y-%m-%dT%H:%M:%S.%f').timestamp())))

            average_tat += completion_time
            
            if completion_time <= (3 * 60 * 60):
                stat['0-3'] += 1 
            if completion_time > (3 * 60 * 60) and completion_time <= (6 * 60 * 60):
                stat['4-6'] += 1 
            if completion_time > (6 * 60 * 60):
                stat['>6'] += 1 

        stat['average_tat'] = int((average_tat / stat['rates_count']))

    stats = sorted(stats, key = lambda x: x['rates_count'])

    return stats