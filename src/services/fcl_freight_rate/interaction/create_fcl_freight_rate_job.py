from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJobs
from services.fcl_freight_rate.models.fcl_freight_rate_jobs_mapping import FclFreightRateJobsMapping
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
from libs.task_distribution_system import task_distribution_system
from database.rails_db import get_user
from fastapi.encoders import jsonable_encoder
from database.db_session import db
from  configs.global_constants import POSSIBLE_SOURCES_IN_JOB_MAPPINGS


def create_fcl_freight_rate_job(request, source):
    with db.atomic():
      return execute_transaction_code(request, source)

def execute_transaction_code(request, source):
    request = jsonable_encoder(request)
    params = {
        'origin_port_id' : request.get('origin_port_id'),
        'origin_main_port_id' : request.get('origin_main_port_id'),
        'destination_port_id' : request.get('destination_port_id'),
        'destination_main_port_id' : request.get('destination_main_port_id'),
        'shipping_line_id' : request.get('shipping_line_id'),
        'service_provider_id' : request.get('service_provider_id'),
        'container_size' : request.get('container_size'),
        'container_type' : request.get('container_type'),
        'commodity' : request.get('commodity'),
        'sources' : [source],
        'rate_type' : request.get('rate_type'),
    }
    init_key = f'{str(params.get("origin_port_id") or "")}:{str(params.get("origin_main_port_id") or "")}:{str(params.get("destination_port_id") or "")}:{str(params.get("destination_main_port_id") or "")}:{str(params.get("shipping_line_id") or "")}:{str(params.get("service_provider_id") or "")}:{str(params.get("container_size") or  "")}:{str(params.get("container_type") or "")}:{str(params.get("commodity") or "")}:{str(params.get("rate_type") or "")}'
    fcl_freight_rate_job = FclFreightRateJobs.select().where(FclFreightRateJobs.init_key == init_key, FclFreightRateJobs.status << ['backlog', 'pending']).first()
    params['init_key'] = init_key

    if not fcl_freight_rate_job:
        fcl_freight_rate_job = create_job_object(params)
    else:
        previous_sources = fcl_freight_rate_job.sources
        if source not in previous_sources and source in POSSIBLE_SOURCES_IN_JOB_MAPPINGS:
            fcl_freight_rate_job.sources = previous_sources + [source]
            fcl_freight_rate_job.save()
            set_jobs_mapping(fcl_freight_rate_job.id, request, source)
        return {"id": fcl_freight_rate_job.id}

    user_id = task_distribution_system('FCL')
    fcl_freight_rate_job.assigned_to_id = user_id
    fcl_freight_rate_job.assigned_to = get_user(user_id)[0]
    fcl_freight_rate_job.status = 'pending'
    fcl_freight_rate_job.set_locations()
    fcl_freight_rate_job.save()
    set_jobs_mapping(fcl_freight_rate_job.id, request, source)
    get_multiple_service_objects(fcl_freight_rate_job)

    return {"id": fcl_freight_rate_job.id}

def set_jobs_mapping(jobs_id, request, source):
    audit_id = FclFreightRateJobsMapping.create(
        source_id=request.get("rate_id"),
        job_id= jobs_id,
        source = source
    )
    return audit_id

def create_job_object(params):
    fcl_freight_rate_job = FclFreightRateJobs()
    for key in list(params.keys()):
        setattr(fcl_freight_rate_job, key, params[key])
    return fcl_freight_rate_job
