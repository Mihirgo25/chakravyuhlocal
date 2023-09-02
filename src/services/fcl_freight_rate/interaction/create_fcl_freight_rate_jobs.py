from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJobs
from services.fcl_freight_rate.models.fcl_freight_rate_jobs_mapping import FclFreightRateJobsMapping
from datetime import datetime, timedelta
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
from services.envision.helpers.task_distribution_system import task_distribution_system
from database.rails_db import get_user
from fastapi.encoders import jsonable_encoder
from database.db_session import db


def create_fcl_freight_rate_jobs(request, source):
    with db.atomic():
      return create_fcl_freight_rate_job(request, source)

def create_fcl_freight_rate_job(request, source):
    updated_ids = []
    request = jsonable_encoder(request)
    for data in request:
        params = {
            'origin_port_id' : data.get('origin_port_id'),
            'destination_port_id' : data.get('destination_port_id'),
            'shipping_line_id' : data.get('shipping_line_id'),
            'service_provider_id' : data.get('service_provider_id'),
            'container_size' : data.get('container_size'),
            'container_type' : data.get('container_type'),
            'commodity' : data.get('commodity'),
            'source' : source,
            'rate_type' : data.get('rate_type'),
            'rate_id' : data.get('rate_id'),
        }
        init_key = f'{str(params.get("origin_port_id"))}:{str(params["destination_port_id"] or "")}:{str(params["shipping_line_id"])}:{str(params["service_provider_id"] or "")}:{str(params["container_size"])}:{str(params["container_type"])}:{str(params["commodity"])}:{str(params["source"])}:{str(params["rate_type"])}:{str(params["rate_id"] or "")}'
        fcl_freight_rate_job = FclFreightRateJobs.select().where(FclFreightRateJobs.init_key == init_key, FclFreightRateJobs.status in ['backlog', 'pending']).first()
        params['init_key'] = init_key

        if not fcl_freight_rate_job:
            fcl_freight_rate_job = create_job_object(params)


        user_id = task_distribution_system('FCL')
        fcl_freight_rate_job.assigned_to_id = user_id
        fcl_freight_rate_job.assigned_to = get_user(user_id)[0]
        fcl_freight_rate_job.status = 'pending'
        fcl_freight_rate_job.set_locations()
        fcl_freight_rate_job.save()
        set_jobs_mapping(fcl_freight_rate_job.id, data)
        get_multiple_service_objects(fcl_freight_rate_job)
        updated_ids.append(fcl_freight_rate_job.id)

    return {"updated_ids": updated_ids}

def set_jobs_mapping(jobs_id, data):
    audit_id = FclFreightRateJobsMapping.create(
        source_id=data.get("rate_id"),
        job_id= jobs_id,
        source = 'fcl_freight_rate',
    )
    return audit_id

def create_job_object(params):
    fcl_freight_rate_job = FclFreightRateJobs()
    for key in list(params.keys()):
        setattr(fcl_freight_rate_job, key, params[key])
    return fcl_freight_rate_job
