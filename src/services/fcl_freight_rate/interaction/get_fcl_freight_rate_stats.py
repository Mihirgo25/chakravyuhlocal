from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from services.fcl_freight_rate.models.fcl_freight_rate_task import FclFreightRateTask
from playhouse.shortcuts import model_to_dict
from rails_client import client
from datetime import datetime, timedelta
from peewee import fn

def get_fcl_freight_rate_stats(request):
    response = {}
    
    for stats_type in request.stats_type:
        response[stats_type] = eval("get_{}_stats()".format(stats_type))

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
        FclFreightRateTask.completed_at >= datetime.strptime(request.validity_start, '%Y-%m-%d') and FclFreightRateTask.completed_at <=  (datetime.strptime(request.validity_end, '%Y-%m-%d') + timedelta(days = 1))
        ).group_by(FclFreightRateTask.completed_by_id)

    stats = [model_to_dict(item) for item in tasks]
    
    if not stats:
        return stats 

    user_ids = list(set([t['performed_by_id'] for t in stats]))
    users = client.ruby.list_users({'filters': {'id': user_ids }, 'return_query': True, 'page_limit': MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT})['list']
    
    users = [{'id':user['id'], 'name':user['name'], 'email':user['name'], 'mobile_number_eformat':user['name']} for user in users]
    users = {user['id']: user for user in users}

    average_tat = 0

    for stat in stats:
        stat['performed_by'] = users[stat['performed_by_id']]

        average_tat = 0.0
        stat['0-3'] = 0
        stat['4-6'] = 0
        stat['>6'] = 0
        
        for tat in stat['tats']: 
            completion_time = (int(round(tat['completed_at'].timestamp())) - int(round(tat['created_at'].timestamp())))

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