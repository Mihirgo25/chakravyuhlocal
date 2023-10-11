from services.ftl_freight_rate.models.ftl_freight_rate_jobs import FtlFreightRateJob
from configs.ftl_freight_rate_constants import FTL_FREIGHT_COVERAGE_USERS
from database.db_session import rd
from micro_services.client import common
from peewee import fn

def allocate_ftl_freight_rate_job(source, service_provider_id):
    
    redis_key = "last_assigned_user_ftl_freight"
    
    if source == 'live_booking':
        live_booking_user = allocate_live_booking_job(service_provider_id) 
        if live_booking_user:
            rd.set(redis_key, live_booking_user)
            return live_booking_user

    
    last_assigned_user = rd.get(redis_key)
    if not last_assigned_user:
        last_assigned_user = 0
    else:
        last_assigned_user = int(last_assigned_user)
    next_user = (last_assigned_user + 1) % len(FTL_FREIGHT_COVERAGE_USERS)
    
    agent_filters = {}
    filters = {"agent_id": FTL_FREIGHT_COVERAGE_USERS}
    agent_filters['filters'] = filters
    online_users = common.list_chat_agents(agent_filters)

    if online_users:
        online_users = online_users['list']

    active_ftl_users = []
    for user in online_users:
        if user['status'] == 'active':
            active_ftl_users.append(user['agent_id'])
            
    if not active_ftl_users:
        rd.set(redis_key, next_user)
        return FTL_FREIGHT_COVERAGE_USERS[next_user]

    query = (FtlFreightRateJob.select(FtlFreightRateJob.user_id, fn.Count(FtlFreightRateJob.user_id).alias('user_id_count'))
            .where((FtlFreightRateJob.user_id << active_ftl_users) &
                    (FtlFreightRateJob.status.not_in(['completed', 'aborted'])))
            .group_by(FtlFreightRateJob.user_id)
            .order_by(fn.Count(FtlFreightRateJob.user_id)))
    
    results = list(query.dicts())
    for i, user in enumerate(results):
        results[i] = str(results[i]['user_id'])
    
    new_users = [user for user in active_ftl_users if user not in results]
    
    if new_users:
        next_user = new_users[0]
    else:
        next_user = results[0]
    
    rd.set(redis_key, next_user)
    return next_user
    
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
    
    