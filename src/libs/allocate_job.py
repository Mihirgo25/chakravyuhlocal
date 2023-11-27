from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJob
from services.fcl_freight_rate.models.fcl_freight_rate_local_job import FclFreightRateLocalJob
from services.air_freight_rate.models.air_freight_rate_jobs import AirFreightRateJob
from services.air_freight_rate.models.air_freight_rate_local_job import AirFreightRateLocalJob
from services.fcl_customs_rate.models.fcl_customs_rate_jobs import FclCustomsRateJob
from services.air_customs_rate.models.air_customs_rate_jobs import AirCustomsRateJob
from services.lcl_freight_rate.models.lcl_freight_rate_jobs import LclFreightRateJob
from services.lcl_customs_rate.models.lcl_customs_rate_jobs import LclCustomsRateJob
from services.haulage_freight_rate.models.haulage_freight_rate_jobs import HaulageFreightRateJob
from services.ltl_freight_rate.models.ltl_freight_rate_jobs import LtlFreightRateJob
from services.ftl_freight_rate.models.ftl_freight_rate_jobs import FtlFreightRateJob
from services.fcl_cfs_rate.models.fcl_cfs_rate_jobs import FclCfsRateJob

from configs.fcl_freight_rate_constants import FCL_EXPORT_COVERAGE_USERS, FCL_IMPORT_COVERAGE_USERS
from configs.fcl_customs_rate_constants import FCL_CUSTOMS_COVERAGE_USERS
from services.air_freight_rate.constants.air_freight_rate_constants import AIR_COVERAGE_USERS
from services.air_customs_rate.air_customs_rate_constants import AIR_CUSTOMS_COVERAGE_USERS
from configs.lcl_freight_rate_constants import LCL_FREIGHT_COVERAGE_USERS
from configs.lcl_customs_rate_constants import LCL_CUSTOMS_COVERAGE_USERS
from configs.haulage_freight_rate_constants import HAULAGE_FREIGHT_COVERAGE_USERS
from configs.ltl_freight_rate_constants import LTL_FREIGHT_COVERAGE_USERS
from configs.ftl_freight_rate_constants import FTL_FREIGHT_COVERAGE_USERS
from configs.fcl_cfs_rate_constants import FCL_CFS_COVERAGE_USERS

from database.db_session import rd
from datetime import datetime
from micro_services.client import common
from peewee import fn

service_info = {
    'fcl_freight':{'model':FclFreightRateJob},
    'fcl_freight_local':{'model':FclFreightRateLocalJob},
    'fcl_customs':{'model':FclCustomsRateJob, 'users':FCL_CUSTOMS_COVERAGE_USERS, 'redis_key':'last_assigned_user_fcl_customs'},
    'air_freight':{'model':AirFreightRateJob, 'users':AIR_COVERAGE_USERS, 'redis_key':'last_assigned_user_air'},
    'air_freight_local':{'model':AirFreightRateLocalJob, 'users':AIR_COVERAGE_USERS, 'redis_key':'last_assigned_user_air_local'},
    'air_customs':{'model':AirCustomsRateJob, 'users':AIR_CUSTOMS_COVERAGE_USERS, 'redis_key':'last_assigned_user_air_customs'},
    'lcl_freight':{'model':LclFreightRateJob, 'users':LCL_FREIGHT_COVERAGE_USERS, 'redis_key':'last_assigned_user_lcl_freight'},
    'lcl_customs':{'model':LclCustomsRateJob, 'users':LCL_CUSTOMS_COVERAGE_USERS, 'redis_key':'last_assigned_user_lcl_customs'},
    'haulage_freight':{'model':HaulageFreightRateJob, 'users':HAULAGE_FREIGHT_COVERAGE_USERS, 'redis_key':'last_assigned_user_fcl_export'},
    'ltl_freight':{'model':LtlFreightRateJob, 'users':LTL_FREIGHT_COVERAGE_USERS, 'redis_key':'last_assigned_user_ltl_freight'},
    'ftl_freight':{'model':FtlFreightRateJob, 'users':FTL_FREIGHT_COVERAGE_USERS, 'redis_key':'last_assigned_user_ftl_freight'},
    'fcl_cfs':{'model':FclCfsRateJob, 'users':FCL_CFS_COVERAGE_USERS, 'redis_key':'last_assigned_user_fcl_cfs'}, 
    
}

def allocate_job(source, service_provider_id, trade_type, service_name):
    """
    Allocate jobs to online users based on job load of users for the given service.
    If no users are online then job is allocated according to round robin method.
    In case source is 'live booking' job is allocated to the user who has been allocated the job with same service provider as this one.
    
    Parameters
    :source (str): The source of the job request.
    :service_provider_id (str): The unique identifier of the service provider.
    :trade_type (str): The type of trade associated with the job.
    :service_name (str): The name of the service associated with the job.
    :return: The allocated user
    :rtype: str
    """
    
    model = service_info[service_name]['model']
    users = []
    redis_key = ""
    
    if service_name in ['fcl_freight', 'fcl_freight_local']:
        if trade_type == "export":
            users = FCL_EXPORT_COVERAGE_USERS
            redis_key = "last_assigned_user_fcl_export" if service_name == 'fcl_freight' else 'last_assigned_user_fcl_local_export'
        else:
            users = FCL_IMPORT_COVERAGE_USERS
            redis_key = "last_assigned_user_fcl_import" if service_name == 'fcl_freight' else 'last_assigned_user_fcl_local_import'
    else:
        users = service_info[service_name]['users']
        redis_key = service_info[service_name]['redis_key']
    
    last_assigned_user = rd.get(redis_key)
    last_assigned_user = int(last_assigned_user) if last_assigned_user else 0
    
    if source == 'live_booking':
        live_booking_user = allocate_live_booking_job(service_provider_id, model) 
        if live_booking_user:
            return live_booking_user

    active_users = get_active_users(users)
            
    if not active_users:
        next_user = (last_assigned_user + 1) % len(users)
        rd.set(redis_key, next_user)
        return users[next_user]
    
    users_by_job_load = get_users_by_job_load(active_users, model)

    new_users = [user for user in active_users if user not in users_by_job_load]
    next_user_id = new_users[0] if new_users else users_by_job_load[0]
    next_user = users.index(next_user_id)
    rd.set(redis_key, next_user)
    
    return next_user_id
    
def allocate_live_booking_job(service_provider_id, model):
    
    query = (model
            .select(model.user_id)
            .distinct()
            .where(
                (model.sources.contains(['live_booking'])) &
                (model.service_provider_id == service_provider_id) &
                (model.status.not_in(['completed', 'aborted'])) &
                (model.updated_at.cast('date') > datetime(2023, 10, 25).date())
            ))
    user_ids = [job.user_id for job in query]
    if user_ids:
        return str(user_ids[0])
    else:
        return None
    
def get_active_users(users):
    
    agent_filters = {}
    filters = {"agent_id": users}
    agent_filters['filters'] = filters
    online_users = common.list_chat_agents(agent_filters)
    
    active_users = []
    if isinstance(online_users, dict) and online_users.get('list'):
        online_users = online_users['list']
    
        for user in online_users:
            if user['status'] == 'active':
                active_users.append(user['agent_id'])
            
    return active_users

def get_users_by_job_load(active_users, model):
    
    query = (model.select(model.user_id, fn.Count(model.user_id).alias('user_id_count'))
            .where((model.user_id << active_users) &
                    (model.status.not_in(['completed', 'aborted'])) & 
                    (model.updated_at.cast('date') > datetime(2023, 10, 25).date()))
            .group_by(model.user_id)
            .order_by(fn.Count(model.user_id)))
    
    results = list(query.dicts())
    for i, user in enumerate(results):
        results[i] = str(results[i]['user_id'])
        
    return results