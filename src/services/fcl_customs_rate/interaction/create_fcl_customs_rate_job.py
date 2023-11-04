from services.fcl_customs_rate.models.fcl_customs_rate_jobs import FclCustomsRateJob
from services.fcl_customs_rate.models.fcl_customs_rate_job_mappings import FclCustomsRateJobMapping
from libs.get_multiple_service_objects import get_multiple_service_objects
from database.rails_db import get_user
from fastapi.encoders import jsonable_encoder
from database.db_session import db
from  configs.global_constants import POSSIBLE_SOURCES_IN_JOB_MAPPINGS
from services.fcl_customs_rate.models.fcl_customs_rate_audit import FclCustomsRateAudit
from configs.env import DEFAULT_USER_ID
from services.fcl_customs_rate.helpers.allocate_fcl_customs_rate_job import allocate_fcl_customs_rate_job



def create_fcl_customs_rate_job(request, source):
    with db.atomic():
      return execute_transaction_code(request, source)

def execute_transaction_code(request, source):
    from services.fcl_customs_rate.fcl_customs_celery_worker import update_live_booking_visiblity_for_fcl_customs_rate_job_delay
    request = jsonable_encoder(request)
    params = {
        'location_id' : request.get('location_id') or request.get('port_id'),
        'service_provider_id' : request.get('service_provider_id'),
        'container_size' : request.get('container_size'),
        'container_type' : request.get('container_type'),
        'commodity' : request.get('commodity'),
        'trade_type': request.get('trade_type'),
        'sources' : [source],
        'rate_type' : request.get('rate_type'),
        'search_source': request.get('source'),
        'is_visible': request.get('is_visible', True),
        'shipment_id': request.get('shipment_id')
    }
    init_key = f'{str(params.get("location_id") or "")}:{str(params.get("service_provider_id") or "")}:{str(params.get("container_size") or  "")}:{str(params.get("container_type") or "")}:{str(params.get("commodity") or "")}:{str(params.get("trade_type") or "")}:{str(params.get("rate_type") or "")}:{str(params.get("shipment_id") or "")}:{str(params.get("cargo_handling_type") or "")}'
    fcl_customs_rate_job = FclCustomsRateJob.select().where(FclCustomsRateJob.init_key == init_key, FclCustomsRateJob.status << ['backlog', 'pending']).first()
    params['init_key'] = init_key

    if not fcl_customs_rate_job:
        fcl_customs_rate_job = create_job_object(params)
        user_id = allocate_fcl_customs_rate_job(source, params['service_provider_id'])
        fcl_customs_rate_job.user_id = user_id
        fcl_customs_rate_job.assigned_to = get_user(user_id)[0]
        fcl_customs_rate_job.status = 'pending'
        fcl_customs_rate_job.set_locations()
        fcl_customs_rate_job.save()
        set_jobs_mapping(fcl_customs_rate_job.id, request, source)
        create_audit(fcl_customs_rate_job.id, request)
        get_multiple_service_objects(fcl_customs_rate_job)
        if source == 'live_booking':
            update_live_booking_visiblity_for_fcl_customs_rate_job_delay.apply_async(args=[fcl_customs_rate_job.id], countdown=1800,queue='critical')

        return {"id": fcl_customs_rate_job.id}

    previous_sources = fcl_customs_rate_job.sources
    if source not in previous_sources and source in POSSIBLE_SOURCES_IN_JOB_MAPPINGS:
        fcl_customs_rate_job.sources = previous_sources + [source]
        set_jobs_mapping(fcl_customs_rate_job.id, request, source)
    fcl_customs_rate_job.status = 'pending'
    fcl_customs_rate_job.is_visible = params['is_visible']
    fcl_customs_rate_job.save()
    if source == 'live_booking':
        update_live_booking_visiblity_for_fcl_customs_rate_job_delay.apply_async(args=[fcl_customs_rate_job.id], countdown=1800,queue='critical')
    create_audit(fcl_customs_rate_job.id, request)
    return {"id": fcl_customs_rate_job.id}


def set_jobs_mapping(jobs_id, request, source):
    mapping_id = FclCustomsRateJobMapping.create(
        source_id=request.get("source_id"),
        shipment_id=request.get("shipment_id"),
        shipment_serial_id = request.get("shipment_serial_id"),
        shipment_service_id = request.get("service_id"),
        job_id= jobs_id,
        source = source,
        status = "pending"
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

def update_live_booking_visiblity_for_fcl_customs_rate_job(job_id):    
    FclCustomsRateJob.update(is_visible=True).where((FclCustomsRateJob.id == job_id) & (FclCustomsRateJob.status == 'pending')).execute()