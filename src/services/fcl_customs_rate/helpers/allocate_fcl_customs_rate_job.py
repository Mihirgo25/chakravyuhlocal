from services.fcl_customs_rate.models.fcl_customs_rate_jobs import FclCustomsRateJob
from configs.fcl_customs_rate_constants import FCL_CUSTOMS_COVERAGE_USERS
from datetime import datetime
from database.db_session import rd
from micro_services.client import common
from peewee import fn

def allocate_fcl_customs_rate_job(source, service_provider_id):
    
    redis_key = "last_assigned_user_fcl_customs"
    last_assigned_user = rd.get(redis_key)
    last_assigned_user = int(last_assigned_user) if last_assigned_user else 0
    
    if source == 'live_booking':
        live_booking_user = allocate_live_booking_job(service_provider_id) 
        if live_booking_user:
            return live_booking_user

    active_fcl_customs_users = get_active_users()
            
    if not active_fcl_customs_users:
        next_user = (last_assigned_user + 1) % len(FCL_CUSTOMS_COVERAGE_USERS)
        rd.set(redis_key, next_user)
        return FCL_CUSTOMS_COVERAGE_USERS[next_user]
    
    users_by_job_load = get_users_by_job_load(active_fcl_customs_users)
    
    new_users = [user for user in active_fcl_customs_users if user not in users_by_job_load]
    next_user_id = new_users[0] if new_users else users_by_job_load[0]
    next_user = FCL_CUSTOMS_COVERAGE_USERS.index(next_user_id)
    rd.set(redis_key, next_user)
   
    return next_user_id
    
def allocate_live_booking_job(service_provider_id):
    
    query = (FclCustomsRateJob
            .select(FclCustomsRateJob.user_id)
            .distinct()
            .where(
                (FclCustomsRateJob.sources.contains(['live_booking'])) &
                (FclCustomsRateJob.service_provider_id == service_provider_id) &
                (FclCustomsRateJob.status.not_in(['completed', 'aborted'])) &
                (FclCustomsRateJob.updated_at.cast('date') > datetime(2023, 10, 24).date())
            ))
    user_ids = [job.user_id for job in query]
    if user_ids:
        return str(user_ids[0])
    else:
        return None

def get_active_users():
    
    agent_filters = {}
    filters = {"agent_id": FCL_CUSTOMS_COVERAGE_USERS}
    agent_filters['filters'] = filters
    online_users = common.list_chat_agents(agent_filters)
    if online_users:
        online_users = online_users['list']
    
    active_users = []
    for user in online_users:
        if user['status'] == 'active':
            active_users.append(user['agent_id'])
            
    return active_users

def get_users_by_job_load(active_users):
    
    query = (FclCustomsRateJob.select(FclCustomsRateJob.user_id, fn.Count(FclCustomsRateJob.user_id).alias('user_id_count'))
            .where((FclCustomsRateJob.user_id << active_users) &
                    (FclCustomsRateJob.status.not_in(['completed', 'aborted'])) &
                    (FclCustomsRateJob.updated_at.cast('date') > datetime(2023, 10, 24).date()))
            .group_by(FclCustomsRateJob.user_id)
            .order_by(fn.Count(FclCustomsRateJob.user_id)))
    
    results = list(query.dicts())
    for i, user in enumerate(results):
        results[i] = str(results[i]['user_id'])
        
    return results
    
    