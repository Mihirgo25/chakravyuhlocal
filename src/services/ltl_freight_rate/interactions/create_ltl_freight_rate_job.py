from services.ltl_freight_rate.models.ltl_freight_rate_jobs import LtlFreightRateJob
from services.ltl_freight_rate.models.ltl_freight_rate_job_mappings import LtlFreightRateJobMapping
from libs.get_multiple_service_objects import get_multiple_service_objects
from libs.allocate_jobs import allocate_jobs
from database.rails_db import get_user
from fastapi.encoders import jsonable_encoder
from database.db_session import db
from configs.global_constants import POSSIBLE_SOURCES_IN_JOB_MAPPINGS
from services.ltl_freight_rate.models.ltl_freight_rate_audit import LtlFreightRateAudit
from configs.env import DEFAULT_USER_ID
from services.ltl_freight_rate.helpers.allocate_ltl_freight_rate_job import allocate_ltl_freight_rate_job


def create_ltl_freight_rate_job(request, source):
    with db.atomic():
      return execute_transaction_code(request, source)

def execute_transaction_code(request, source):
    from services.ltl_freight_rate.ltl_celery_worker import update_live_booking_visiblity_for_ltl_freight_rate_job_delay
    request = jsonable_encoder(request)
    params = {
        'origin_location_id' : request.get('origin_location_id'),
        'destination_location_id' : request.get('destination_location_id'),
        'service_provider_id' : request.get('service_provider_id'),
        'commodity' : request.get('commodity'),
        'trip_type': request.get('trip_type'),
        'transit_time' : request.get('transit_time'),
        'density_factor' : request.get('density_factor'),
        'sources' : [source],
        'rate_type' : request.get('rate_type'),
        'search_source': request.get('source'),
        'is_visible': request.get('is_visible', True),
    }
    init_key = f'{str(params.get("origin_location_id") or "")}:{str(params.get("destination_location_id") or "")}:{str(params.get("service_provider_id") or "")}:{str(params.get("commodity") or  "")}:{str(params.get("trip_type") or "")}:{str(params.get("transit_time") or "")}:{str(params.get("density_factor") or "")}:{str(params.get("rate_type") or "")}'
    ltl_freight_rate_job = LtlFreightRateJob.select().where(LtlFreightRateJob.init_key == init_key, LtlFreightRateJob.status << ['backlog', 'pending']).first()
    params['init_key'] = init_key

    if not ltl_freight_rate_job:
        ltl_freight_rate_job = create_job_object(params)
        user_id = allocate_ltl_freight_rate_job(source, params['service_provider_id'])
        ltl_freight_rate_job.user_id = user_id
        ltl_freight_rate_job.assigned_to = get_user(user_id)[0]
        ltl_freight_rate_job.status = 'pending'
        ltl_freight_rate_job.set_locations()
        ltl_freight_rate_job.save()
        set_jobs_mapping(ltl_freight_rate_job.id, request, source)
        create_audit(ltl_freight_rate_job.id, request)
        get_multiple_service_objects(ltl_freight_rate_job)
        if source == 'live_booking':
            update_live_booking_visiblity_for_ltl_freight_rate_job_delay.apply_async(args=[ltl_freight_rate_job.id], countdown=1800,queue='fcl_freight_rate')

        return {"id": ltl_freight_rate_job.id}
    
    previous_sources = ltl_freight_rate_job.sources
    if source not in previous_sources and source in POSSIBLE_SOURCES_IN_JOB_MAPPINGS:
        ltl_freight_rate_job.sources = previous_sources + [source]
        ltl_freight_rate_job.save()
        set_jobs_mapping(ltl_freight_rate_job.id, request, source)
        create_audit(ltl_freight_rate_job.id, request)
    return {"id": ltl_freight_rate_job.id}


def set_jobs_mapping(jobs_id, request, source):
    mapping_id = LtlFreightRateJobMapping.create(
        source_id=request.get("source_id"),
        shipment_id=request.get("shipment_id"),
        job_id= jobs_id,
        source = source,
        status = 'pending'
    )
    return mapping_id

def create_job_object(params):
    ltl_freight_rate_job = LtlFreightRateJob()
    for key in list(params.keys()):
        setattr(ltl_freight_rate_job, key, params[key])
    return ltl_freight_rate_job


def create_audit(jobs_id, request):
    LtlFreightRateAudit.create(
        action_name = 'create',
        object_id = jobs_id,
        object_type = 'LtlFreightRateJob',
        data = request,
        performed_by_id = DEFAULT_USER_ID
    )
    
def update_live_booking_visiblity_for_ltl_freight_rate_job(job_id):    
    LtlFreightRateJob.update(is_visible=True).where((LtlFreightRateJob.id == job_id) & (LtlFreightRateJob.status == 'pending')).execute()