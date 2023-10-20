from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJob
from services.fcl_freight_rate.models.fcl_freight_rate_job_mappings import FclFreightRateJobMapping
from libs.get_multiple_service_objects import get_multiple_service_objects
from libs.allocate_jobs import allocate_jobs
from database.rails_db import get_user
from fastapi.encoders import jsonable_encoder
from database.db_session import db
from  configs.global_constants import POSSIBLE_SOURCES_IN_JOB_MAPPINGS
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
from configs.env import DEFAULT_USER_ID
from services.fcl_freight_rate.helpers.allocate_fcl_freight_rate_job import allocate_fcl_freight_rate_job



def create_fcl_freight_rate_job(request, source):
    object_type = "Fcl_Freight_Rate_Job"
    query = "create table if not exists fcl_services_audits_{} partition of fcl_services_audits for values in ('{}')".format(
        object_type.lower(), object_type.replace("_", "")
    )
    db.execute_sql(query)
    with db.atomic():
      return execute_transaction_code(request, source)

def execute_transaction_code(request, source):
    from services.fcl_freight_rate.fcl_celery_worker import update_live_booking_visiblity_for_fcl_freight_rate_job_delay
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
        'search_source': request.get('source'),
        'is_visible': request.get('is_visible', True),
        'shipment_id': request.get('shipment_id')
    }
    init_key = f'{str(params.get("origin_port_id") or "")}:{str(params.get("origin_main_port_id") or "")}:{str(params.get("destination_port_id") or "")}:{str(params.get("destination_main_port_id") or "")}:{str(params.get("shipping_line_id") or "")}:{str(params.get("service_provider_id") or "")}:{str(params.get("container_size") or  "")}:{str(params.get("container_type") or "")}:{str(params.get("commodity") or "")}:{str(params.get("rate_type") or "")}:{str(params.get("shipment_id") or "")}'
    fcl_freight_rate_job = FclFreightRateJob.select().where(FclFreightRateJob.init_key == init_key, FclFreightRateJob.status << ['backlog', 'pending']).first()
    params['init_key'] = init_key

    if not fcl_freight_rate_job:
        fcl_freight_rate_job = create_job_object(params)
        user_id = allocate_fcl_freight_rate_job(source, params['service_provider_id'])
        fcl_freight_rate_job.user_id = user_id
        fcl_freight_rate_job.assigned_to = get_user(user_id)[0]
        fcl_freight_rate_job.status = 'pending'
        fcl_freight_rate_job.set_locations()
        fcl_freight_rate_job.save()
        set_jobs_mapping(fcl_freight_rate_job.id, request, source)
        create_audit(fcl_freight_rate_job.id, request)
        get_multiple_service_objects(fcl_freight_rate_job)
        if source == 'live_booking':
            update_live_booking_visiblity_for_fcl_freight_rate_job_delay.apply_async(args=[fcl_freight_rate_job.id], countdown=1800,queue='critical')

        return {"id": fcl_freight_rate_job.id}
    
    previous_sources = fcl_freight_rate_job.sources
    if source not in previous_sources and source in POSSIBLE_SOURCES_IN_JOB_MAPPINGS:
        fcl_freight_rate_job.sources = previous_sources + [source]
        set_jobs_mapping(fcl_freight_rate_job.id, request, source)

    fcl_freight_rate_job.status = 'pending'
    fcl_freight_rate_job.is_visible = params['is_visible']
    fcl_freight_rate_job.save()
    if source == 'live_booking':
            update_live_booking_visiblity_for_fcl_freight_rate_job_delay.apply_async(args=[fcl_freight_rate_job.id], countdown=1800,queue='critical')
    create_audit(fcl_freight_rate_job.id, request)

    return {"id": fcl_freight_rate_job.id}


def set_jobs_mapping(jobs_id, request, source):
    mapping_id = FclFreightRateJobMapping.create(
        source_id=request.get("source_id"),
        shipment_id=request.get("shipment_id"),
        shipment_serial_id = request.get("shipment_serial_id"),
        shipment_service_id = request.get("service_id"),
        job_id= jobs_id,
        source = source,
        status = 'pending',
    )
    return mapping_id

def create_job_object(params):
    fcl_freight_rate_job = FclFreightRateJob()
    for key in list(params.keys()):
        setattr(fcl_freight_rate_job, key, params[key])
    return fcl_freight_rate_job


def create_audit(jobs_id, request):
    FclServiceAudit.create(
        action_name = 'create',
        object_id = jobs_id,
        object_type = 'FclFreightRateJob',
        data = request,
        performed_by_id = DEFAULT_USER_ID
    )
    
def update_live_booking_visiblity_for_fcl_freight_rate_job(job_id):    
    FclFreightRateJob.update(is_visible=True).where((FclFreightRateJob.id == job_id) & (FclFreightRateJob.status == 'pending')).execute()

