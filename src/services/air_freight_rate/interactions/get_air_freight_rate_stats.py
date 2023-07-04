from datetime import timedelta,datetime
from fastapi import HTTPException
from peewee import fn
import json 
from services.air_freight_rate.models.air_freight_rate_tasks import AirFreightRateTasks
from database.rails_db import get_user

def get_air_freight_rate_stats(request):
    response={}
    for stats_type in request['stats_types']:
        try:
            response[stats_type]=eval(f"get_{stats_type}_stats(request)")
        except Exception as e:
            print(e)
            response[stats_type]=None
    return response

def get_tech_ops_dashboard_stats(request):
    tasks=AirFreightRateTasks.select(AirFreightRateTasks.completed_by_id.alias('performed_by_id'),
            fn.COUNT(AirFreightRateTasks.id).alias('rates_count'),
            fn.SUM(AirFreightRateTasks.source_count).alias('shipments_count'),
            fn.json_agg(fn.json_build_object(
        'created_at',AirFreightRateTasks.created_at,
        'completed_at',AirFreightRateTasks.completed_at
            )).alias("tats")).where(AirFreightRateTasks.status=='completed').where(AirFreightRateTasks.completed_at>=request['validity_start'].date(),AirFreightRateTasks.completed_at<=(request['validity_end'].date()+timedelta(days=1))).group_by(AirFreightRateTasks.completed_by_id)
    stats=list(tasks.dicts())

    if not stats:
        return stats
    
    user_ids=list(set([t['performed_by_id'] for t in stats]))
    users=get_user(user_ids)

    users=[{'id':str(user['id']),'name':user['name'],'email':user['email'],'mobile_number_eformat':user['mobile_number_eformat']}for user in users]

    users={user['id']:user for user in users}

    average_tat=0

    for stat in stats:
        try:
            stat['performed_by'] = users[str(stat['performed_by_id'])]
        except:
            stat['performed_by'] = None
        average_tat=0.0
        stat['0-3'] = 0
        stat['4-6'] = 0
        stat['>6'] = 0

        for tat in stat['tats']:
            completion_time = (int(round(datetime.fromisoformat(tat['completed_at']).timestamp())) - int(round(datetime.strptime(tat['created_at'], '%Y-%m-%dT%H:%M:%S.%f').timestamp())))

            average_tat+=completion_time

            if completion_time <= (3 * 60 * 60):
                stat['0-3'] += 1 
            if completion_time > (3 * 60 * 60) and completion_time <= (6 * 60 * 60):
                stat['4-6'] += 1 
            if completion_time > (6 * 60 * 60):
                stat['>6'] += 1 
        stat['average_tat']=int((average_tat / stat['rates_count']))
    stats=sorted(stats,key =lambda x:x['rates_count'])
    return stats
