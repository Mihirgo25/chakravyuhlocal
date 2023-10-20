from services.ftl_freight_rate.models.ftl_freight_rate_jobs import FtlFreightRateJob
from services.ftl_freight_rate.models.ftl_freight_rate_job_mappings import FtlFreightRateJobMapping
from libs.get_multiple_service_objects import get_multiple_service_objects
from libs.allocate_jobs import allocate_jobs
from database.rails_db import get_user
from fastapi.encoders import jsonable_encoder
from database.db_session import db
from  configs.global_constants import POSSIBLE_SOURCES_IN_JOB_MAPPINGS
from services.ftl_freight_rate.models.ftl_freight_rate_audit import FtlFreightRateAudit
from configs.env import DEFAULT_USER_ID
from services.ftl_freight_rate.helpers.allocate_ftl_freight_rate_job import allocate_ftl_freight_rate_job

def create_ftl_freight_rate_job(request, source):
    with db.atomic():
      return execute_transaction_code(request, source)

def execute_transaction_code(request, source):
    from services.ftl_freight_rate.ftl_celery_worker import update_live_booking_visiblity_for_ftl_freight_rate_job_delay
    request = jsonable_encoder(request)
    params = {
        'origin_location_id' : request.get('origin_location_id'),
        'destination_location_id' : request.get('destination_location_id'),
        'service_provider_id' : request.get('service_provider_id'),
        'truck_type' : request.get('truck_type'),
        'truck_body_type' : request.get('truck_body_type'),
        'trip_type' : request.get('trip_type'),
        'commodity' : request.get('commodity'),
        'transit_time' : request.get('transit_time'),
        'detention_free_time' : request.get('detention_free_time'),
        'unit' : request.get('unit'),
        'sources' : [source],
        'rate_type' : request.get('rate_type'),
        'search_source': request.get('source'),
        'is_visible': request.get('is_visible', True),
        'shipment_id': request.get('shipment_id')
    }
    init_key = f'{str(params.get("origin_location_id") or "")}:{str(params.get("destination_location_id") or "")}:{str(params.get("service_provider_id") or "")}:{str(params.get("truck_type") or "")}:{str(params.get("truck_body_type") or "")}:{str(params.get("trip_type") or  "")}:{str(params.get("commodity") or "")}:{str(params.get("transit_time") or "")}:{str(params.get("detention_free_time") or "")}:{str(params.get("unit") or "")}:{str(params.get("rate_type") or "")}:{str(params.get("shipment_id") or "")}'
    ftl_freight_rate_job = FtlFreightRateJob.select().where(FtlFreightRateJob.init_key == init_key, FtlFreightRateJob.status << ['backlog', 'pending']).first()
    params['init_key'] = init_key
    if not ftl_freight_rate_job:
        ftl_freight_rate_job = create_job_object(params)
        user_id = allocate_ftl_freight_rate_job(source, params['service_provider_id'])
        ftl_freight_rate_job.user_id = user_id
        ftl_freight_rate_job.assigned_to = get_user(user_id)[0]
        ftl_freight_rate_job.status = 'pending'
        ftl_freight_rate_job.set_locations()
        ftl_freight_rate_job.save()
        set_jobs_mapping(ftl_freight_rate_job.id, request, source)
        create_audit(ftl_freight_rate_job.id, request)
        get_multiple_service_objects(ftl_freight_rate_job)
        if source == 'live_booking':
            update_live_booking_visiblity_for_ftl_freight_rate_job_delay.apply_async(args=[ftl_freight_rate_job.id], countdown=1800,queue='fcl_freight_rate')

        return {"id": ftl_freight_rate_job.id}

    previous_sources = ftl_freight_rate_job.sources
    if source not in previous_sources and source in POSSIBLE_SOURCES_IN_JOB_MAPPINGS:
        ftl_freight_rate_job.sources = previous_sources + [source]
        set_jobs_mapping(ftl_freight_rate_job.id, request, source)
    
    ftl_freight_rate_job.status = 'pending'
    ftl_freight_rate_job.is_visible = params['is_visible']
    ftl_freight_rate_job.save()
    if source == 'live_booking':
        update_live_booking_visiblity_for_ftl_freight_rate_job_delay.apply_async(args=[ftl_freight_rate_job.id], countdown=1800,queue='fcl_freight_rate')
    create_audit(ftl_freight_rate_job.id, request)
    return {"id": ftl_freight_rate_job.id}


def set_jobs_mapping(jobs_id, request, source):
    mapping_id = FtlFreightRateJobMapping.create(
        source_id=request.get("source_id"),
        shipment_id=request.get("shipment_id"),
        shipment_serial_id = request.get("shipment_serial_id"),
        job_id= jobs_id,
        source = source,
        status = 'pending'
    )
    return mapping_id

def create_job_object(params):
    ftl_freight_rate_job = FtlFreightRateJob()
    for key in list(params.keys()):
        setattr(ftl_freight_rate_job, key, params[key])
    return ftl_freight_rate_job


def create_audit(jobs_id, request):
    FtlFreightRateAudit.create(
        action_name = 'create',
        object_id = jobs_id,
        object_type = 'FtlFreightRateJob',
        data = request,
        performed_by_id = DEFAULT_USER_ID
    )

def update_live_booking_visiblity_for_ftl_freight_rate_job(job_id):    
    FtlFreightRateJob.update(is_visible=True).where((FtlFreightRateJob.id == job_id) & (FtlFreightRateJob.status == 'pending')).execute()