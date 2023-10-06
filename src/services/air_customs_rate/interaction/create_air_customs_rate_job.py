from services.air_customs_rate.models.air_customs_rate_jobs import AirCustomsRateJob
from services.air_customs_rate.models.air_customs_rate_job_mappings import AirCustomsRateJobMapping
from libs.get_multiple_service_objects import get_multiple_service_objects
from libs.allocate_jobs import allocate_jobs
from fastapi.encoders import jsonable_encoder
from database.rails_db import get_user
from database.db_session import db
from configs.global_constants import POSSIBLE_SOURCES_IN_JOB_MAPPINGS
from services.air_customs_rate.models.air_customs_rate_audit import AirCustomsRateAudit
from configs.env import DEFAULT_USER_ID


def create_air_customs_rate_job(request, source):
    with db.atomic():
      return execute_transaction_code(request, source)


def execute_transaction_code(request, source):

    request = jsonable_encoder(request)

    params = {
        'airport_id' : request.get('airport_id'),
        'service_provider_id' : request.get('service_provider_id'),
        'commodity' : request.get('commodity'),
        'sources' : [source],
        'rate_type' : request.get('rate_type'),
        'trade_type': request.get('trade_type'),
        'search_source': request.get('source'),
    }
    
    init_key = f'{str(params.get("airport_id") or "")}:{str(params.get("service_provider_id") or "")}:{str(params.get("commodity") or "")}:{str(params.get("rate_type") or "")}:{str(params.get("trade_type") or "")}'
    air_customs_rate_job = AirCustomsRateJob.select().where(AirCustomsRateJob.init_key == init_key, AirCustomsRateJob.status << ['backlog', 'pending']).first()
    params['init_key'] = init_key

    if not air_customs_rate_job:
        air_customs_rate_job = create_job_object(params)
        user_id = allocate_jobs('AIR_CUSTOMS')
        air_customs_rate_job.user_id = user_id
        air_customs_rate_job.assigned_to = get_user(user_id)[0]
        air_customs_rate_job.status = 'pending'
        air_customs_rate_job.set_locations()
        air_customs_rate_job.save()
        set_jobs_mapping(air_customs_rate_job.id, request, source)
        create_audit(air_customs_rate_job.id, request)
        get_multiple_service_objects(air_customs_rate_job)

        return {"id": air_customs_rate_job.id}
    
    previous_sources = air_customs_rate_job.sources
    if source not in previous_sources and source in POSSIBLE_SOURCES_IN_JOB_MAPPINGS:
        air_customs_rate_job.sources = previous_sources + [source]
        air_customs_rate_job.save()
        set_jobs_mapping(air_customs_rate_job.id, request, source)
        create_audit(air_customs_rate_job.id, request)
    return {"id": air_customs_rate_job.id}


def set_jobs_mapping(jobs_id, request, source):
    mapping_id = AirCustomsRateJobMapping.create(
        source_id=request.get("source_id"),
        job_id= jobs_id,
        source = source,
        status = "pending"
    )
    return mapping_id

def create_job_object(params):
    air_customs_rate_job = AirCustomsRateJob()
    for key in list(params.keys()):
        setattr(air_customs_rate_job, key, params[key])
    return air_customs_rate_job

def create_audit(jobs_id, request):
    AirCustomsRateAudit.create(
        action_name = 'create',
        object_id = jobs_id,
        object_type = 'AirCustomsRateJob',
        data = request,
        performed_by_id = DEFAULT_USER_ID
    )