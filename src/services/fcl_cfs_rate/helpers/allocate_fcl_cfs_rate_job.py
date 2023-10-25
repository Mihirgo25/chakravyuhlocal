from services.fcl_cfs_rate.models.fcl_cfs_rate_jobs import FclCfsRateJob
from configs.fcl_cfs_rate_constants import FCL_CFS_COVERAGE_USERS
from database.db_session import rd
from micro_services.client import common
from peewee import fn
from datetime import datetime

def allocate_fcl_cfs_rate_job(source, service_provider_id):
    
    redis_key = "last_assigned_user_fcl_cfs"
    last_assigned_user = rd.get(redis_key)
    last_assigned_user = int(last_assigned_user) if last_assigned_user else 0
    
    if source == 'live_booking':
        live_booking_user = allocate_live_booking_job(service_provider_id) 
        if live_booking_user:
            return live_booking_user

    active_fcl_cfs_users = get_active_users()
            
    if not active_fcl_cfs_users:
        next_user = (last_assigned_user + 1) % len(FCL_CFS_COVERAGE_USERS)
        rd.set(redis_key, next_user)
        return FCL_CFS_COVERAGE_USERS[next_user]

    users_by_job_load = get_users_by_job_load(active_fcl_cfs_users)
    
    new_users = [user for user in active_fcl_cfs_users if user not in users_by_job_load]
    next_user_id = new_users[0] if new_users else users_by_job_load[0]
    next_user = FCL_CFS_COVERAGE_USERS.index(next_user_id)
    rd.set(redis_key, next_user)
    
    return next_user_id
    
def allocate_live_booking_job(service_provider_id):
    
    query = (FclCfsRateJob
            .select(FclCfsRateJob.user_id)
            .distinct()
            .where(
                (FclCfsRateJob.sources.contains(['live_booking'])) &
                (FclCfsRateJob.service_provider_id == service_provider_id) &
                (FclCfsRateJob.status.not_in(['completed', 'aborted'])) &
                (FclCfsRateJob.updated_at.cast('date') > datetime(2023, 10, 25).date())
            ))
    user_ids = [job.user_id for job in query]
    if user_ids:
        return str(user_ids[0])
    else:
        return None

def get_active_users():
    
    agent_filters = {}
    filters = {"agent_id": FCL_CFS_COVERAGE_USERS}
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
    
    query = (FclCfsRateJob.select(FclCfsRateJob.user_id, fn.Count(FclCfsRateJob.user_id).alias('user_id_count'))
            .where((FclCfsRateJob.user_id << active_users) &
                    (FclCfsRateJob.status.not_in(['completed', 'aborted'])) &
                    (FclCfsRateJob.updated_at.cast('date') > datetime(2023, 10, 25).date()))
            .group_by(FclCfsRateJob.user_id)
            .order_by(fn.Count(FclCfsRateJob.user_id)))
    
    results = list(query.dicts())
    for i, user in enumerate(results):
        results[i] = str(results[i]['user_id'])
        
    return results
    
    