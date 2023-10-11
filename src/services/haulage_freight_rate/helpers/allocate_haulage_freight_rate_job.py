from services.haulage_freight_rate.models.haulage_freight_rate_jobs import HaulageFreightRateJob
from configs.haulage_freight_rate_constants import HAULAGE_FREIGHT_COVERAGE_USERS
from database.db_session import rd
from micro_services.client import common
from peewee import fn

def allocate_haulage_freight_rate_job(source, service_provider_id):
    
    redis_key = "last_assigned_user_haulage_freight"
    
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
    next_user = (last_assigned_user + 1) % len(HAULAGE_FREIGHT_COVERAGE_USERS)
    
    agent_filters = {}
    filters = {"agent_id": HAULAGE_FREIGHT_COVERAGE_USERS}
    agent_filters['filters'] = filters
    online_users = common.list_chat_agents(agent_filters)

    if online_users:
        online_users = online_users['list']

    active_haulage_users = []
    for user in online_users:
        if user['status'] == 'active':
            active_haulage_users.append(user['agent_id'])
            
    if not active_haulage_users:
        rd.set(redis_key, next_user)
        return HAULAGE_FREIGHT_COVERAGE_USERS[next_user]

    query = (HaulageFreightRateJob.select(HaulageFreightRateJob.user_id, fn.Count(HaulageFreightRateJob.user_id).alias('user_id_count'))
            .where((HaulageFreightRateJob.user_id << active_haulage_users) &
                    (HaulageFreightRateJob.status.not_in(['completed', 'aborted'])))
            .group_by(HaulageFreightRateJob.user_id)
            .order_by(fn.Count(HaulageFreightRateJob.user_id)))
    
    results = list(query.dicts())
    for i, user in enumerate(results):
        results[i] = str(results[i]['user_id'])
    
    new_users = [user for user in active_haulage_users if user not in results]
    
    if new_users:
        next_user = new_users[0]
    else:
        next_user = results[0]
    
    rd.set(redis_key, next_user)
    return next_user
    
def allocate_live_booking_job(service_provider_id):
    
    query = (HaulageFreightRateJob
            .select(HaulageFreightRateJob.user_id)
            .distinct()
            .where(
                (HaulageFreightRateJob.sources.contains(['live_booking'])) &
                (HaulageFreightRateJob.service_provider_id == service_provider_id) &
                (HaulageFreightRateJob.status.not_in(['completed', 'aborted']))
            ))
    user_ids = [job.user_id for job in query]
    if user_ids:
        return str(user_ids[0])
    else:
        return None
    
    