from services.fcl_cfs_rate.models.fcl_cfs_rate_jobs import FclCfsRateJob
from services.fcl_cfs_rate.models.fcl_cfs_rate_job_mappings import FclCfsRateJobMapping
from libs.get_multiple_service_objects import get_multiple_service_objects
from libs.allocate_jobs import allocate_jobs
from database.rails_db import get_user
from fastapi.encoders import jsonable_encoder
from database.db_session import db
from  configs.global_constants import POSSIBLE_SOURCES_IN_JOB_MAPPINGS
from services.fcl_cfs_rate.models.fcl_cfs_rate_audit import FclCfsRateAudit
from configs.env import DEFAULT_USER_ID



def create_fcl_cfs_rate_job(request, source):
    with db.atomic():
      return execute_transaction_code(request, source)

def execute_transaction_code(request, source):
    request = jsonable_encoder(request)
    params = {
        'location_id' : request.get('port_id'),
        'service_provider_id' : request.get('service_provider_id'),
        'container_size' : request.get('container_size'),
        'container_type' : request.get('container_type'),
        'commodity' : request.get('commodity'),
        'sources' : [source],
        'trade_type': request.get('trade_type'),
        'rate_type' : request.get('rate_type'),
        'search_source': request.get('source'),
    }
    init_key = f'{str(params.get("location_id") or "")}:{str(params.get("service_provider_id") or "")}:{str(params.get("container_size") or  "")}:{str(params.get("container_type") or "")}:{str(params.get("commodity") or "")}:{str(params.get("rate_type") or "")}'
    fcl_cfs_rate_job = FclCfsRateJob.select().where(FclCfsRateJob.init_key == init_key, FclCfsRateJob.status << ['backlog', 'pending']).first()
    params['init_key'] = init_key

    if not fcl_cfs_rate_job:
        fcl_cfs_rate_job = create_job_object(params)
        user_id = allocate_jobs('FCL_CFS')
        fcl_cfs_rate_job.user_id = user_id
        fcl_cfs_rate_job.assigned_to = get_user(user_id)[0]
        fcl_cfs_rate_job.status = 'pending'
        fcl_cfs_rate_job.set_locations()
        fcl_cfs_rate_job.save()
        set_jobs_mapping(fcl_cfs_rate_job.id, request, source)
        create_audit(fcl_cfs_rate_job.id, request)
        get_multiple_service_objects(fcl_cfs_rate_job)

        return {"id": fcl_cfs_rate_job.id}
    
    previous_sources = fcl_cfs_rate_job.sources
    if source not in previous_sources and source in POSSIBLE_SOURCES_IN_JOB_MAPPINGS:
        fcl_cfs_rate_job.sources = previous_sources + [source]
        fcl_cfs_rate_job.save()
        set_jobs_mapping(fcl_cfs_rate_job.id, request, source)
        create_audit(fcl_cfs_rate_job.id, request)
    return {"id": fcl_cfs_rate_job.id}


def set_jobs_mapping(jobs_id, request, source):
    mapping_id = FclCfsRateJobMapping.create(
        source_id=request.get("source_id"),
        shipment_id=request.get("shipment_id"),
        job_id= jobs_id,
        source = source,
        status = "pending"
    )
    return mapping_id

def create_job_object(params):
    fcl_cfs_rate_job = FclCfsRateJob()
    for key in list(params.keys()):
        setattr(fcl_cfs_rate_job, key, params[key])
    return fcl_cfs_rate_job


def create_audit(jobs_id, request):
    FclCfsRateAudit.create(
        action_name = 'create',
        object_id = jobs_id,
        object_type = 'FclCfsRateJob',
        data = request,
        performed_by_id = DEFAULT_USER_ID
    )