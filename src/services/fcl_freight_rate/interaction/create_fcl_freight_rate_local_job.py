from services.fcl_freight_rate.models.fcl_freight_rate_local_jobs import (
    FclFreightRateLocalJob,
)
from services.fcl_freight_rate.models.fcl_freight_rate_local_job_mappings import (
    FclFreightRateLocalJobMapping,
)
from services.fcl_freight_rate.helpers.get_multiple_service_objects import (
    get_multiple_service_objects,
)
from libs.allocate_jobs import allocate_jobs
from database.rails_db import get_user
from fastapi.encoders import jsonable_encoder
from database.db_session import db
from configs.global_constants import POSSIBLE_SOURCES_IN_JOB_MAPPINGS
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
from configs.env import DEFAULT_USER_ID


def create_fcl_freight_rate_local_job(request, source):
    object_type = "Fcl_Freight_Rate_Local_Job"
    query = "create table if not exists fcl_services_audits_{} partition of fcl_services_audits for values in ('{}')".format(
        object_type.lower(), object_type.replace("_", "")
    )
    db.execute_sql(query)
    with db.atomic():
        return execute_transaction_code(request, source)


def execute_transaction_code(request, source):
    request = jsonable_encoder(request)
    params = {
        "port_id": request.get("port_id"),
        "main_port_id": request.get("main_port_id"),
        "shipping_line_id": request.get("shipping_line_id"),
        "service_provider_id": request.get("service_provider_id"),
        "container_size": request.get("container_size"),
        "container_type": request.get("container_type"),
        "commodity": request.get("commodity"),
        "trade_type": request.get("trade_type"),
        "rate_type": request.get("rate_type"),
    }
    init_key = f'{str(params.get("port_id") or "")}:{str(params.get("main_port_id") or "")}:{str(params.get("shipping_line_id") or "")}:{str(params.get("service_provider_id") or "")}:{str(params.get("container_size") or  "")}:{str(params.get("container_type") or "")}:{str(params.get("commodity") or "")}:{str(params.get("trade_type") or "")}:{str(params.get("rate_type") or "")}'
    fcl_freight_rate_local_job = (
        FclFreightRateLocalJob.select()
        .where(
            FclFreightRateLocalJob.init_key == init_key,
            FclFreightRateLocalJob.status << ["backlog", "pending"],
        )
        .first()
    )
    params["init_key"] = init_key

    if not fcl_freight_rate_local_job:
        fcl_freight_rate_local_job = create_job_object(params)
        user_id = allocate_jobs("FCL_LOCALS")
        fcl_freight_rate_local_job.user_id = user_id
        fcl_freight_rate_local_job.assigned_to = get_user(user_id)[0]
        fcl_freight_rate_local_job.status = "pending"
        fcl_freight_rate_local_job.save()
        set_jobs_mapping(fcl_freight_rate_local_job.id, request, source)
        create_audit(fcl_freight_rate_local_job.id, request)
        get_multiple_service_objects(fcl_freight_rate_local_job)

        return {"id": fcl_freight_rate_local_job.id}

    previous_sources = fcl_freight_rate_local_job.sources
    if source not in previous_sources and source in POSSIBLE_SOURCES_IN_JOB_MAPPINGS:
        fcl_freight_rate_local_job.sources = previous_sources + [source]
        fcl_freight_rate_local_job.save()
        set_jobs_mapping(fcl_freight_rate_local_job.id, request, source)
        create_audit(fcl_freight_rate_local_job.id, request)
    return {"id": fcl_freight_rate_local_job.id}


def set_jobs_mapping(jobs_id, request, source):
    mapping_id = FclFreightRateLocalJobMapping.create(
        source_id=request.get("source_id"),
        job_id=jobs_id,
        source=source,
        status="pending",
    )
    return mapping_id


def create_job_object(params):
    fcl_freight_rate_local_job = FclFreightRateLocalJob()
    for key in list(params.keys()):
        setattr(fcl_freight_rate_local_job, key, params[key])
    return fcl_freight_rate_local_job


def create_audit(jobs_id, request):
    FclServiceAudit.create(
        action_name="create",
        object_id=jobs_id,
        object_type="FclFreightRateLocalJob",
        data=request,
        performed_by_id=DEFAULT_USER_ID,
    )
