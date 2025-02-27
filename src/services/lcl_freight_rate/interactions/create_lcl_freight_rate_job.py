from services.lcl_freight_rate.models.lcl_freight_rate_jobs import LclFreightRateJob
from services.lcl_freight_rate.models.lcl_freight_rate_job_mappings import (
    LclFreightRateJobMapping,
)
from libs.get_multiple_service_objects import get_multiple_service_objects
from database.rails_db import get_user
from fastapi.encoders import jsonable_encoder
from database.db_session import db
from configs.global_constants import POSSIBLE_SOURCES_IN_JOB_MAPPINGS
from services.lcl_freight_rate.models.lcl_freight_rate_audit import LclFreightRateAudit
from configs.env import DEFAULT_USER_ID
from libs.allocate_job import allocate_job


def create_lcl_freight_rate_job(request, source):
    with db.atomic():
        return execute_transaction_code(request, source)


def execute_transaction_code(request, source):
    from services.lcl_freight_rate.lcl_celery_worker import update_live_booking_visiblity_for_lcl_freight_rate_job_delay
    request = jsonable_encoder(request)
    params = {
        "origin_port_id": request.get("origin_port_id"),
        "destination_port_id": request.get("destination_port_id"),
        "service_provider_id": request.get("service_provider_id"),
        "commodity": request.get("commodity"),
        "sources": [source],
        "rate_type": request.get("rate_type"),
        'search_source': request.get('source'),
        'is_visible': request.get('is_visible', True),
        'shipment_id': request.get('shipment_id'),
        'source_id': request.get('source_id')
    }
    init_key = f'{str(params.get("origin_port_id") or "")}:{str(params.get("destination_port_id") or "")}:{str(params.get("destination_port_id") or "")}:{str(params.get("service_provider_id") or "")}:{str(params.get("commodity") or  "")}:{str(params.get("rate_type") or "")}:{str(params.get("shipment_id") or "")}:{str(params.get("source_id") or "")}'
    lcl_freight_rate_job = (
        LclFreightRateJob.select()
        .where(
            LclFreightRateJob.init_key == init_key,
            LclFreightRateJob.status << ["backlog", "pending"],
        )
        .first()
    )
    params["init_key"] = init_key

    if not lcl_freight_rate_job:
        lcl_freight_rate_job = create_job_object(params)
        user_id = allocate_job(source, params['service_provider_id'], 'lcl_freight')
        lcl_freight_rate_job.user_id = user_id
        lcl_freight_rate_job.assigned_to = get_user(user_id)[0]
        lcl_freight_rate_job.status = "pending"
        lcl_freight_rate_job.set_locations()
        lcl_freight_rate_job.save()
        set_jobs_mapping(lcl_freight_rate_job.id, request, source)
        create_audit(lcl_freight_rate_job.id, request)
        get_multiple_service_objects(lcl_freight_rate_job)
        if source == 'live_booking':
            update_live_booking_visiblity_for_lcl_freight_rate_job_delay.apply_async(args=[lcl_freight_rate_job.id], countdown=1800,queue='critical')

        return {"id": lcl_freight_rate_job.id}

    previous_sources = lcl_freight_rate_job.sources
    if source not in previous_sources and source in POSSIBLE_SOURCES_IN_JOB_MAPPINGS:
        lcl_freight_rate_job.sources = previous_sources + [source]
        set_jobs_mapping(lcl_freight_rate_job.id, request, source)
    
    lcl_freight_rate_job.status = 'pending'
    lcl_freight_rate_job.is_visible = params['is_visible']
    lcl_freight_rate_job.save()
    if source == 'live_booking':
        update_live_booking_visiblity_for_lcl_freight_rate_job_delay.apply_async(args=[lcl_freight_rate_job.id], countdown=1800,queue='critical')
    create_audit(lcl_freight_rate_job.id, request)
    return {"id": lcl_freight_rate_job.id}


def set_jobs_mapping(jobs_id, request, source):
    mapping_id = LclFreightRateJobMapping.create(
        source_id=request.get("source_id"),
        shipment_id=request.get("shipment_id"),
        source_serial_id = request.get("serial_id"),
        shipment_service_id = request.get("service_id"),
        job_id=jobs_id,
        source=source,
        status="pending",
    )
    return mapping_id


def create_job_object(params):
    lcl_freight_rate_job = LclFreightRateJob()
    for key in list(params.keys()):
        setattr(lcl_freight_rate_job, key, params[key])
    return lcl_freight_rate_job


def create_audit(jobs_id, request):
    LclFreightRateAudit.create(
        action_name="create",
        object_id=jobs_id,
        object_type="LclFreightRateJob",
        data=request,
        performed_by_id=DEFAULT_USER_ID,
    )

def update_live_booking_visiblity_for_lcl_freight_rate_job(job_id):    
    LclFreightRateJob.update(is_visible=True).where((LclFreightRateJob.id == job_id) & (LclFreightRateJob.status == 'pending')).execute()