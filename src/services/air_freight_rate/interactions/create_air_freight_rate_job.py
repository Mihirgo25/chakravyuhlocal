from datetime import datetime, timedelta
from services.air_freight_rate.models.air_freight_rate_jobs import AirFreightRateJobs
from services.air_freight_rate.models.air_freight_rate_jobs_mapping import AirFreightRateJobsMapping
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
from services.envision.helpers.task_distribution_system import task_distribution_system
from fastapi.encoders import jsonable_encoder
from database.rails_db import get_user
from database.db_session import db



def create_air_freight_rate_job(request, source):
    with db.atomic():
      return execute_transaction_code(request, source)


def execute_transaction_code(request, source):

    request = jsonable_encoder(request)

    params = {
        'origin_airport_id' : request.get('origin_airport_id'),
        'destination_airport_id' : request.get('destination_airport_id'),
        'airline_id' : request.get('airline_id'),
        'service_provider_id' : request.get('service_provider_id'),
        'commodity' : request.get('commodity'),
        'source' : source,
        'rate_type' : request.get('rate_type'),
        'rate_id' : request.get('rate_id'),
        'commodity_type': request.get('commodity_type'),
        'commodity_sub_type': request.get('commodity_sub_type'),
        'operation_type': request.get('operation_type'),
        'shipment_type': request.get('shipment_type'),
        'stacking_type': request.get('stacking_type'),
        'price_type': request.get('price_type')
    }
    
    init_key = f'{str(params.get("origin_airport_id"))}:{str(params.get("destination_airport_id") or "")}:{str(params.get("airline_id"))}:{str(params.get("service_provider_id") or "")}:{str(params.get("commodity"))}:{str(params.get("rate_type"))}:{str(params.get("commodity_type") or "")}:{str(params.get("commodity_sub_type") or "")}:{str(params.get("stacking_type") or "")}:{str(params.get("operation_type") or "")}'
    air_freight_rate_job = AirFreightRateJobs.select().where(AirFreightRateJobs.init_key == init_key, AirFreightRateJobs.status << ['backlog', 'pending']).first()
    params['init_key'] = init_key

    if not air_freight_rate_job:
        air_freight_rate_job = create_job_object(params)
    else:
        return {"id": air_freight_rate_job.id}

    user_id = task_distribution_system('AIR')
    air_freight_rate_job.assigned_to_id = user_id
    air_freight_rate_job.assigned_to = get_user(user_id)
    air_freight_rate_job.status = 'pending'
    air_freight_rate_job.set_locations()
    air_freight_rate_job.save()
    set_jobs_mapping(air_freight_rate_job.id, request)
    get_multiple_service_objects(air_freight_rate_job)

    return {"updated_ids": air_freight_rate_job.id}

def set_jobs_mapping(jobs_id, request):
    audit_id = AirFreightRateJobsMapping.create(
        source_id=request.get("rate_id"),
        job_id= jobs_id,
        source = 'air_freight_rate'
    )
    return audit_id

def create_job_object(params):
    air_freight_rate_job = AirFreightRateJobs()
    for key in list(params.keys()):
        setattr(air_freight_rate_job, key, params[key])
    return air_freight_rate_job