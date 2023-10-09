from services.lcl_customs_rate.models.lcl_customs_rate_jobs import LclCustomsRateJob
from services.lcl_customs_rate.models.lcl_customs_rate_job_mappings import (
    LclCustomsRateJobMapping,
)
from libs.get_multiple_service_objects import get_multiple_service_objects

from libs.allocate_jobs import allocate_jobs
from database.rails_db import get_user
from fastapi.encoders import jsonable_encoder
from database.db_session import db
from configs.global_constants import POSSIBLE_SOURCES_IN_JOB_MAPPINGS
from services.lcl_customs_rate.models.lcl_customs_rate_audit import LclCustomsRateAudit
from configs.env import DEFAULT_USER_ID


def create_lcl_customs_rate_job(request, source):
    with db.atomic():
        return execute_transaction_code(request, source)


def execute_transaction_code(request, source):
    request = jsonable_encoder(request)
    params = {
        "location_id": request.get("location_id"),
        "service_provider_id": request.get("service_provider_id"),
        "importer_exporter_id": request.get("importer_exporter_id"),
        "container_size": request.get("container_size"),
        "container_type": request.get("container_type"),
        "commodity": request.get("commodity"),
        "sources": [source],
        "rate_type": request.get("rate_type"),
        'search_source': request.get('source'),
    }
    init_key = f'{str(params.get("location_id") or "")}:{str(params.get("service_provider_id") or "")}:{str(params.get("importer_exporter_id") or "")}:{str(params.get("container_size") or  "")}:{str(params.get("container_type") or "")}:{str(params.get("commodity") or "")}:{str(params.get("rate_type") or "")}'
    lcl_customs_rate_job = (
        LclCustomsRateJob.select()
        .where(
            LclCustomsRateJob.init_key == init_key,
            LclCustomsRateJob.status << ["backlog", "pending"],
        )
        .first()
    )
    params["init_key"] = init_key

    if not lcl_customs_rate_job:
        lcl_customs_rate_job = create_job_object(params)
        user_id = allocate_jobs("LCL_CUSTOMS")
        lcl_customs_rate_job.user_id = user_id
        lcl_customs_rate_job.assigned_to = get_user(user_id)[0]
        lcl_customs_rate_job.status = "pending"
        lcl_customs_rate_job.set_locations()
        lcl_customs_rate_job.save()
        set_jobs_mapping(lcl_customs_rate_job.id, request, source)
        create_audit(lcl_customs_rate_job.id, request)
        get_multiple_service_objects(lcl_customs_rate_job)

        return {"id": lcl_customs_rate_job.id}

    previous_sources = lcl_customs_rate_job.sources
    if source not in previous_sources and source in POSSIBLE_SOURCES_IN_JOB_MAPPINGS:
        lcl_customs_rate_job.sources = previous_sources + [source]
        lcl_customs_rate_job.save()
        set_jobs_mapping(lcl_customs_rate_job.id, request, source)
        create_audit(lcl_customs_rate_job.id, request)
    return {"id": lcl_customs_rate_job.id}


def set_jobs_mapping(jobs_id, request, source):
    mapping_id = LclCustomsRateJobMapping.create(
        source_id=request.get("source_id"),
        shipment_id=request.get("shipment_id"),
        job_id=jobs_id,
        source=source,
        status="pending",
    )
    return mapping_id


def create_job_object(params):
    lcl_customs_rate_job = LclCustomsRateJob()
    for key in list(params.keys()):
        setattr(lcl_customs_rate_job, key, params[key])
    return lcl_customs_rate_job


def create_audit(jobs_id, request):
    LclCustomsRateAudit.create(
        action_name="create",
        object_id=jobs_id,
        object_type="LclCustomsRateJob",
        data=request,
        performed_by_id=DEFAULT_USER_ID,
    )
