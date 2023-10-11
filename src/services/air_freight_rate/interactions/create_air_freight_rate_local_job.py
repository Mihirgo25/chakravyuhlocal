from services.air_freight_rate.models.air_freight_rate_local_jobs import (
    AirFreightRateLocalJob,
)
from services.air_freight_rate.models.air_freight_rate_local_jobs_mapping import (
    AirFreightRateLocalJobMapping,
)
from libs.get_multiple_service_objects import get_multiple_service_objects
from libs.allocate_jobs import allocate_jobs
from fastapi.encoders import jsonable_encoder
from database.rails_db import get_user
from database.db_session import db
from configs.global_constants import POSSIBLE_SOURCES_IN_JOB_MAPPINGS
from services.air_freight_rate.models.air_services_audit import AirServiceAudit
from configs.env import DEFAULT_USER_ID
from services.air_freight_rate.helpers.allocate_air_freight_rate_local_job import allocate_air_freight_rate_local_job


def create_air_freight_rate_local_job(request, source):
    object_type = "Air_Freight_Rate_Local_Job"
    query = "create table if not exists air_services_audits_{} partition of air_services_audits for values in ('{}')".format(
        object_type.lower(), object_type.replace("_", "")
    )
    db.execute_sql(query)
    with db.atomic():
        return execute_transaction_code(request, source)


def execute_transaction_code(request, source):
    request = jsonable_encoder(request)

    params = {
        "airport_id": request.get("airport_id"),
        "airline_id": request.get("airline_id"),
        "trade_type": request.get("trade_type"),
        "service_provider_id": request.get("service_provider_id"),
        "sources": [source],
        "rate_type": request.get("rate_type"),
        "commodity": request.get("commodity"),
        "commodity_type": request.get("commodity_type"),
        "operation_type": request.get("operation_type"),
        "shipment_type": request.get("shipment_type"),
        "stacking_type": request.get("stacking_type"),
        "price_type": request.get("price_type"),
        'search_source': request.get('source'),
        'is_visible': request.get('is_visible') or True,
    }

    init_key = f'{str(params.get("airport_id") or "")}:{str(params.get("airline_id") or "")}:{str(params.get("service_provider_id") or "")}:{str(params.get("commodity") or "")}:{str(params.get("rate_type") or "")}:{str(params.get("commodity_type") or "")}:{str(params.get("stacking_type") or "")}:{str(params.get("operation_type") or "")}'
    air_freight_rate_local_job = (
        AirFreightRateLocalJob.select()
        .where(
            AirFreightRateLocalJob.init_key == init_key,
            AirFreightRateLocalJob.status << ["backlog", "pending"],
        )
        .first()
    )
    params["init_key"] = init_key

    if not air_freight_rate_local_job:
        air_freight_rate_local_job = create_job_object(params)
        user_id = allocate_air_freight_rate_local_job(source, params['service_provider_id'])
        air_freight_rate_local_job.user_id = user_id
        air_freight_rate_local_job.assigned_to = get_user(user_id)[0]
        air_freight_rate_local_job.status = "pending"
        air_freight_rate_local_job.set_locations()
        air_freight_rate_local_job.save()
        set_jobs_mapping(air_freight_rate_local_job.id, request, source)
        create_audit(air_freight_rate_local_job.id, request)
        get_multiple_service_objects(air_freight_rate_local_job)

        return {"id": air_freight_rate_local_job.id}

    previous_sources = air_freight_rate_local_job.sources
    if source not in previous_sources and source in POSSIBLE_SOURCES_IN_JOB_MAPPINGS:
        air_freight_rate_local_job.sources = previous_sources + [source]
        air_freight_rate_local_job.save()
        set_jobs_mapping(air_freight_rate_local_job.id, request, source)
        create_audit(air_freight_rate_local_job.id, request)
    return {"id": air_freight_rate_local_job.id}


def set_jobs_mapping(jobs_id, request, source):
    mapping_id = AirFreightRateLocalJobMapping.create(
        source_id=request.get("source_id"),
        shipment_id=request.get("shipment_id"),
        job_id=jobs_id,
        source=source,
        status="pending",
    )
    return mapping_id


def create_job_object(params):
    air_freight_rate_local_job = AirFreightRateLocalJob()
    for key in list(params.keys()):
        setattr(air_freight_rate_local_job, key, params[key])
    return air_freight_rate_local_job


def create_audit(jobs_id, request):
    AirServiceAudit.create(
        action_name="create",
        object_id=jobs_id,
        object_type="AirFreightRateLocalJob",
        data=request,
        performed_by_id=DEFAULT_USER_ID,
    )
