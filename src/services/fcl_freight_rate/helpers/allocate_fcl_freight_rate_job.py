from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJob
from configs.fcl_freight_rate_constants import FCL_EXPORT_COVERAGE_USERS, FCL_IMPORT_COVERAGE_USERS
from database.db_session import rd
from datetime import datetime
from micro_services.client import common
from peewee import fn

def allocate_fcl_freight_rate_job(source, service_provider_id, trade_type):
    
    fcl_users = []
    if trade_type == "export":
        fcl_users = FCL_EXPORT_COVERAGE_USERS
        redis_key = "last_assigned_user_fcl_export"
    else:
        fcl_users = FCL_IMPORT_COVERAGE_USERS
        redis_key = "last_assigned_user_fcl_import"
    
    
    last_assigned_user = rd.get(redis_key)
    last_assigned_user = int(last_assigned_user) if last_assigned_user else 0
    
    if source == 'live_booking':
        live_booking_user = allocate_live_booking_job(service_provider_id) 
        if live_booking_user:
            return live_booking_user

    active_fcl_users = get_active_users(fcl_users)
            
    if not active_fcl_users:
        next_user = (last_assigned_user + 1) % len(fcl_users)
        rd.set(redis_key, next_user)
        return fcl_users[next_user]
    
    users_by_job_load = get_users_by_job_load(active_fcl_users)

    new_users = [user for user in active_fcl_users if user not in users_by_job_load]
    next_user_id = new_users[0] if new_users else users_by_job_load[0]
    next_user = fcl_users.index(next_user_id)
    rd.set(redis_key, next_user)
    
    return next_user_id
    
def allocate_live_booking_job(service_provider_id):
    
    query = (FclFreightRateJob
            .select(FclFreightRateJob.user_id)
            .distinct()
            .where(
                (FclFreightRateJob.sources.contains(['live_booking'])) &
                (FclFreightRateJob.service_provider_id == service_provider_id) &
                (FclFreightRateJob.status.not_in(['completed', 'aborted'])) &
                (FclFreightRateJob.updated_at.cast('date') > datetime(2023, 10, 24).date())
            ))
    user_ids = [job.user_id for job in query]
    if user_ids:
        return str(user_ids[0])
    else:
        return None
    
def get_active_users(fcl_users):
    
    agent_filters = {}
    filters = {"agent_id": fcl_users}
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
    
    query = (FclFreightRateJob.select(FclFreightRateJob.user_id, fn.Count(FclFreightRateJob.user_id).alias('user_id_count'))
            .where((FclFreightRateJob.user_id << active_users) &
                    (FclFreightRateJob.status.not_in(['completed', 'aborted'])) & 
                    (FclFreightRateJob.updated_at.cast('date') > datetime(2023, 10, 24).date()))
            .group_by(FclFreightRateJob.user_id)
            .order_by(fn.Count(FclFreightRateJob.user_id)))
    
    results = list(query.dicts())
    for i, user in enumerate(results):
        results[i] = str(results[i]['user_id'])
        
    return results
    
    