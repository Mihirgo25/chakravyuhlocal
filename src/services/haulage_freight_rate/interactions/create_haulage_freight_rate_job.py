from services.haulage_freight_rate.models.haulage_freight_rate_jobs import HaulageFreightRateJob
from services.haulage_freight_rate.models.haulage_freight_rate_job_mappings import HaulageFreightRateJobMapping
from libs.get_multiple_service_objects import get_multiple_service_objects
from fastapi.encoders import jsonable_encoder
from database.rails_db import get_user
from database.db_session import db
from configs.global_constants import POSSIBLE_SOURCES_IN_JOB_MAPPINGS
from services.haulage_freight_rate.models.haulage_freight_rate_audit import HaulageFreightRateAudit
from configs.env import DEFAULT_USER_ID
from libs.allocate_job import allocate_job


def create_haulage_freight_rate_job(request, source):
    with db.atomic():
      return execute_transaction_code(request, source)
    
def execute_transaction_code(request, source):
    from services.haulage_freight_rate.haulage_celery_worker import update_live_booking_visiblity_for_haulage_freight_rate_job_delay

    request = jsonable_encoder(request)

    params = {
        'origin_location' : request.get('origin_location'),
        'destination_location' : request.get('destination_location'),
        'origin_location_id' : request.get('origin_location_id'),
        'destination_location_id' : request.get('destination_location_id'),
        'shipping_line_id' : request.get('shipping_line_id'),
        'service_provider_id' : request.get('service_provider_id'),
        'container_size' : request.get('container_size'),
        'container_type' : request.get('container_type'),
        'commodity' : request.get('commodity'),
        'haulage_type': request.get('haulage_type'),
        'trailer_type': request.get('trailer_type'),
        'trip_type': request.get('trip_type'),
        'sources' : [source],
        'transport_modes_keyword': request.get('transport_mode'),
        'rate_type' : request.get('rate_type'),
        'search_source': request.get('source'),
        'is_visible': request.get('is_visible', True),
        'shipment_id': request.get('shipment_id'),
        'source_id': request.get('source_id')
    }

    init_key = f'{str(params.get("origin_location_id") or "")}:{str(params.get("destination_location_id") or "")}:{str(params.get("shipping_line_id") or "")}:{str(params.get("service_provider_id") or "")}:{str(params.get("container_size") or  "")}:{str(params.get("container_type") or "")}:{str(params.get("commodity") or "")}:{str(params.get("haulage_type") or "")}:{str(params.get("trailer_type") or "")}:{str(params.get("transport_modes_keyword") or "")}:{str(params.get("rate_type") or "")}:{str(params.get("shipment_id") or "")}:{str(params.get("source_id") or "")}'
    haulage_freight_rate_job = HaulageFreightRateJob.select().where(HaulageFreightRateJob.init_key == init_key, HaulageFreightRateJob.status << ['backlog', 'pending']).first()
    params['init_key'] = init_key

    if not haulage_freight_rate_job:
        haulage_freight_rate_job = create_job_object(params)
        user_id = allocate_job(source, params['service_provider_id'], None, 'haulage_freight')
        haulage_freight_rate_job.user_id = user_id
        haulage_freight_rate_job.assigned_to = get_user(user_id)[0]
        haulage_freight_rate_job.status = 'pending'
        haulage_freight_rate_job.set_locations()
        haulage_freight_rate_job.save()
        set_jobs_mapping(haulage_freight_rate_job.id, request, source)
        create_audit(haulage_freight_rate_job.id, request)
        get_multiple_service_objects(haulage_freight_rate_job)
        if source == 'live_booking':
            update_live_booking_visiblity_for_haulage_freight_rate_job_delay.apply_async(args=[haulage_freight_rate_job.id], countdown=1800,queue='critical')

        return {"id": haulage_freight_rate_job.id}
    
    previous_sources = haulage_freight_rate_job.sources
    if source not in previous_sources and source in POSSIBLE_SOURCES_IN_JOB_MAPPINGS:
        haulage_freight_rate_job.sources = previous_sources + [source]
        set_jobs_mapping(haulage_freight_rate_job.id, request, source)
    haulage_freight_rate_job.status = 'pending'
    haulage_freight_rate_job.is_visible = params['is_visible']
    haulage_freight_rate_job.save()
    if source == 'live_booking':
        update_live_booking_visiblity_for_haulage_freight_rate_job_delay.apply_async(args=[haulage_freight_rate_job.id], countdown=1800,queue='critical')
    create_audit(haulage_freight_rate_job.id, request)
    return {"id": haulage_freight_rate_job.id}

def set_jobs_mapping(jobs_id, request, source):
    mapping_id = HaulageFreightRateJobMapping.create(
        source_id=request.get("source_id"),
        shipment_id=request.get("shipment_id"),
        source_serial_id = request.get("serial_id"),
        shipment_service_id = request.get("service_id"),
        job_id= jobs_id,
        source = source,
        status = "pending"
    )
    return mapping_id

def create_job_object(params):
    haulage_freight_rate_job = HaulageFreightRateJob()
    for key in list(params.keys()):
        setattr(haulage_freight_rate_job, key, params[key])
    return haulage_freight_rate_job


def create_audit(jobs_id, request):
    HaulageFreightRateAudit.create(
        action_name = 'create',
        object_id = jobs_id,
        object_type = 'HaulageFreightRateJob',
        data = request,
        performed_by_id = DEFAULT_USER_ID
    )

def update_live_booking_visiblity_for_haulage_freight_rate_job(job_id):    
    HaulageFreightRateJob.update(is_visible=True).where((HaulageFreightRateJob.id == job_id) & (HaulageFreightRateJob.status == 'pending')).execute()