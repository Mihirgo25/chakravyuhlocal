from services.fcl_customs_rate.models.fcl_customs_rate_jobs import FclCustomsRateJob
from services.fcl_customs_rate.models.fcl_customs_rate_job_mappings import FclCustomsRateJobMapping
from services.fcl_customs_rate.helpers import get_multiple_service_objects
from libs.allocate_jobs import allocate_jobs
from database.rails_db import get_user
from fastapi.encoders import jsonable_encoder
from database.db_session import db
from  configs.global_constants import POSSIBLE_SOURCES_IN_JOB_MAPPINGS
from services.fcl_customs_rate.models.fcl_customs_rate_audit import FclCustomsRateAudit
from configs.env import DEFAULT_USER_ID



def create_fcl_customs_rate_job(request, source):
    object_type = "Fcl_Customs_Rate_Job"
    query = "create table if not exists fcl_customs_rate_audit_{} partition of fcl_customs_rate_audit for values in ('{}')".format(
        object_type.lower(), object_type.replace("_", "")
    )
    db.execute_sql(query)
    with db.atomic():
      return execute_transaction_code(request, source)

def execute_transaction_code(request, source):
    request = jsonable_encoder(request)
    params = {
        'location_id' : request.get('location_id'),
        'service_provider_id' : request.get('service_provider_id'),
        'container_size' : request.get('container_size'),
        'container_type' : request.get('container_type'),
        'commodity' : request.get('commodity'),
        'sources' : [source],
        'rate_type' : request.get('rate_type'),
    }
    init_key = f'{str(params.get("location_id") or "")}:{str(params.get("service_provider_id") or "")}:{str(params.get("container_size") or  "")}:{str(params.get("container_type") or "")}:{str(params.get("commodity") or "")}:{str(params.get("rate_type") or "")}'
    fcl_customs_rate_job = FclCustomsRateJob.select().where(FclCustomsRateJob.init_key == init_key, FclCustomsRateJob.status << ['backlog', 'pending']).first()
    params['init_key'] = init_key

    if not fcl_customs_rate_job:
        fcl_customs_rate_job = create_job_object(params)
        user_id = allocate_jobs('FCL_CUSTOMS')
        fcl_customs_rate_job.user_id = user_id
        fcl_customs_rate_job.assigned_to = get_user(user_id)[0]
        fcl_customs_rate_job.status = 'pending'
        fcl_customs_rate_job.set_locations()
        fcl_customs_rate_job.save()
        set_jobs_mapping(fcl_customs_rate_job.id, request, source)
        create_audit(fcl_customs_rate_job.id, request)
        get_multiple_service_objects(fcl_customs_rate_job)

        return {"id": fcl_customs_rate_job.id}

    previous_sources = fcl_customs_rate_job.sources
    if source not in previous_sources and source in POSSIBLE_SOURCES_IN_JOB_MAPPINGS:
        fcl_customs_rate_job.sources = previous_sources + [source]
        fcl_customs_rate_job.save()
        set_jobs_mapping(fcl_customs_rate_job.id, request, source)
        create_audit(fcl_customs_rate_job.id, request)
    return {"id": fcl_customs_rate_job.id}


def set_jobs_mapping(jobs_id, request, source):
    mapping_id = FclCustomsRateJobMapping.create(
        source_id=request.get("rate_id"),
        job_id= jobs_id,
        source = source
    )
    return mapping_id

def create_job_object(params):
    fcl_customs_rate_job = FclCustomsRateJob()
    for key in list(params.keys()):
        setattr(fcl_customs_rate_job, key, params[key])
    return fcl_customs_rate_job


def create_audit(jobs_id, request):
    FclCustomsRateAudit.create(
        action_name = 'create',
        object_id = jobs_id,
        object_type = 'FclCustomsRateJob',
        data = request,
        performed_by_id = DEFAULT_USER_ID
    )