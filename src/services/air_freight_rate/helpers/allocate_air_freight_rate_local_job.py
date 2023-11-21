from services.air_freight_rate.models.air_freight_rate_local_jobs import AirFreightRateLocalJob
from services.air_freight_rate.constants.air_freight_rate_constants import AIR_COVERAGE_USERS
from database.db_session import rd
from micro_services.client import common
from datetime import datetime
from peewee import fn

def allocate_air_freight_rate_local_job(source, service_provider_id):
    
    redis_key = "last_assigned_user_air_local"
    last_assigned_user = rd.get(redis_key)
    last_assigned_user = int(last_assigned_user) if last_assigned_user else 0
    
    if source == 'live_booking':
        live_booking_user = allocate_live_booking_job(service_provider_id) 
        if live_booking_user:
            return live_booking_user

    active_air_local_users = get_active_users()
            
    if not active_air_local_users:
        next_user = (last_assigned_user + 1) % len(AIR_COVERAGE_USERS)
        rd.set(redis_key, next_user)
        return AIR_COVERAGE_USERS[next_user]

    users_by_job_load = get_users_by_job_load(active_air_local_users)
    
    new_users = [user for user in active_air_local_users if user not in users_by_job_load]
    next_user_id = new_users[0] if new_users else users_by_job_load[0]
    next_user = AIR_COVERAGE_USERS.index(next_user_id)
    rd.set(redis_key, next_user)
    
    return next_user_id
    
def allocate_live_booking_job(service_provider_id):
    
    query = (AirFreightRateLocalJob
            .select(AirFreightRateLocalJob.user_id)
            .distinct()
            .where(
                (AirFreightRateLocalJob.sources.contains(['live_booking'])) &
                (AirFreightRateLocalJob.service_provider_id == service_provider_id) &
                (AirFreightRateLocalJob.status.not_in(['completed', 'aborted'])) &
                (AirFreightRateLocalJob.updated_at.cast('date') > datetime(2023, 10, 25).date())
            ))
    user_ids = [job.user_id for job in query]
    if user_ids:
        return str(user_ids[0])
    else:
        return None
    
def get_active_users():
    
    agent_filters = {}
    filters = {"agent_id": AIR_COVERAGE_USERS}
    agent_filters['filters'] = filters
    online_users = common.list_chat_agents(agent_filters)
    
    active_users = []
    if isinstance(online_users, dict) and online_users.get('list'):
        online_users = online_users['list']
    
        for user in online_users:
            if user['status'] == 'active':
                active_users.append(user['agent_id'])
            
    return active_users

def get_users_by_job_load(active_users):
    
    query = (AirFreightRateLocalJob.select(AirFreightRateLocalJob.user_id, fn.Count(AirFreightRateLocalJob.user_id).alias('user_id_count'))
            .where((AirFreightRateLocalJob.user_id << active_users) &
                    (AirFreightRateLocalJob.status.not_in(['completed', 'aborted'])) &
                    (AirFreightRateLocalJob.updated_at.cast('date') > datetime(2023, 10, 25).date()))
            .group_by(AirFreightRateLocalJob.user_id)
            .order_by(fn.Count(AirFreightRateLocalJob.user_id)))
    
    results = list(query.dicts())
    for i, user in enumerate(results):
        results[i] = str(results[i]['user_id'])
        
    return results
    
    