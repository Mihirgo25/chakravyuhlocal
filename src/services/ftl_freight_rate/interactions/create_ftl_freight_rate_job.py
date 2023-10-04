from services.ftl_freight_rate.models.ftl_freight_rate_jobs import FtlFreightRateJob
from services.ftl_freight_rate.models.ftl_freight_rate_job_mappings import FtlFreightRateJobMapping
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
from libs.allocate_jobs import allocate_jobs
from database.rails_db import get_user
from fastapi.encoders import jsonable_encoder
from database.db_session import db
from  configs.global_constants import POSSIBLE_SOURCES_IN_JOB_MAPPINGS
from services.ftl_freight_rate.models.ftl_services_audit import FtlServiceAudit
from configs.env import DEFAULT_USER_ID

def create_ftl_freight_rate_job(request, source = "spot_search"):
    object_type = "Ftl_Freight_Rate_Job"
    query = "create table if not exists ftl_services_audits_{} partition of ftl_services_audits for values in ('{}')".format(
        object_type.lower(), object_type.replace("_", "")
    )
    db.execute_sql(query)
    with db.atomic():
      return execute_transaction_code(request, source)

def execute_transaction_code(request, source):
    request = jsonable_encoder(request)
    params = {
        'origin_location_id' : request.get('origin_location_id'),
        'destination_location_id' : request.get('destination_location_id'),
        'importer_exporter_id' : request.get('importer_exporter_id'),
        'service_provider_id' : request.get('service_provider_id'),
        'truck_type' : request.get('truck_type'),
        'truck_body_type' : request.get('truck_body_type'),
        'trip_type' : request.get('trip_type'),
        'commodity_type' : request.get('commodity_type'),
        'sources' : [source],
        'rate_type' : request.get('rate_type'),
    }
    init_key = f'{str(params.get("origin_location_id") or "")}:{str(params.get("destination_location_id") or "")}:{str(params.get("importer_exporter_id") or "")}:{str(params.get("service_provider_id") or "")}:{str(params.get("truck_type") or "")}:{str(params.get("truck_body_type") or "")}:{str(params.get("trip_type") or  "")}:{str(params.get("commodity_type") or "")}:{str(params.get("rate_type") or "")}'
    ftl_freight_rate_job = FtlFreightRateJob.select().where(FtlFreightRateJob.init_key == init_key, FtlFreightRateJob.status << ['backlog', 'pending']).first()
    params['init_key'] = init_key

    if not ftl_freight_rate_job:
        ftl_freight_rate_job = create_job_object(params)
        user_id = allocate_jobs('FTL_FREIGHT')
        ftl_freight_rate_job.user_id = user_id
        ftl_freight_rate_job.assigned_to = get_user(user_id)[0]
        ftl_freight_rate_job.status = 'pending'
        ftl_freight_rate_job.set_locations()
        ftl_freight_rate_job.save()
        set_jobs_mapping(ftl_freight_rate_job.id, request, source)
        # create_audit(ftl_freight_rate_job.id, request)
        get_multiple_service_objects(ftl_freight_rate_job)

        return {"id": ftl_freight_rate_job.id}

    previous_sources = ftl_freight_rate_job.sources
    if source not in previous_sources and source in POSSIBLE_SOURCES_IN_JOB_MAPPINGS:
        ftl_freight_rate_job.sources = previous_sources + [source]
        ftl_freight_rate_job.save()
        set_jobs_mapping(ftl_freight_rate_job.id, request, source)
        create_audit(ftl_freight_rate_job.id, request)
    return {"id": ftl_freight_rate_job.id}


def set_jobs_mapping(jobs_id, request, source):
    mapping_id = FtlFreightRateJobMapping.create(
        source_id=request.get("source_id"),
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
    FtlServiceAudit.create(
        action_name = 'create',
        object_id = jobs_id,
        object_type = 'FtlFreightRateJob',
        data = request,
        performed_by_id = DEFAULT_USER_ID
    )