from services.ftl_freight_rate.models.ftl_freight_rate_jobs import FtlFreightRateJob
from configs.ftl_freight_rate_constants import FTL_FREIGHT_COVERAGE_USERS
from database.db_session import rd
from micro_services.client import common
from peewee import fn

def allocate_ftl_freight_rate_job(source, service_provider_id):
    
    redis_key = "last_assigned_user_ftl_freight"
    last_assigned_user = rd.get(redis_key)
    last_assigned_user = int(last_assigned_user) if last_assigned_user else 0
    
    if source == 'live_booking':
        live_booking_user = allocate_live_booking_job(service_provider_id) 
        if live_booking_user:
            return live_booking_user

    active_ftl_users = get_active_users()

            
    if not active_ftl_users:
        next_user = (last_assigned_user + 1) % len(FTL_FREIGHT_COVERAGE_USERS)
        rd.set(redis_key, next_user)
        return FTL_FREIGHT_COVERAGE_USERS[next_user]

    users_by_job_load = get_users_by_job_load(active_ftl_users)
    
    new_users = [user for user in active_ftl_users if user not in users_by_job_load]
    next_user_id = new_users[0] if new_users else users_by_job_load[0]
    next_user = FTL_FREIGHT_COVERAGE_USERS.index(next_user_id)
    rd.set(redis_key, next_user)
    
    return next_user_id
    
def allocate_live_booking_job(service_provider_id):
    
    query = (FtlFreightRateJob
            .select(FtlFreightRateJob.user_id)
            .distinct()
            .where(
                (FtlFreightRateJob.sources.contains(['live_booking'])) &
                (FtlFreightRateJob.service_provider_id == service_provider_id) &
                (FtlFreightRateJob.status.not_in(['completed', 'aborted']))
            ))
    user_ids = [job.user_id for job in query]
    if user_ids:
        return str(user_ids[0])
    else:
        return None
    
def get_active_users():
    
    agent_filters = {}
    filters = {"agent_id": FTL_FREIGHT_COVERAGE_USERS}
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
    
    query = (FtlFreightRateJob.select(FtlFreightRateJob.user_id, fn.Count(FtlFreightRateJob.user_id).alias('user_id_count'))
            .where((FtlFreightRateJob.user_id << active_users) &
                    (FtlFreightRateJob.status.not_in(['completed', 'aborted'])))
            .group_by(FtlFreightRateJob.user_id)
            .order_by(fn.Count(FtlFreightRateJob.user_id)))
    
    results = list(query.dicts())
    for i, user in enumerate(results):
        results[i] = str(results[i]['user_id'])
        
    return results
    
    