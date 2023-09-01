from datetime import datetime, timedelta
from services.air_freight_rate.models.air_freight_rate_jobs import AirFreightRateJobs
from services.air_freight_rate.models.air_freight_rate_jobs_mapping import AirFreightRateJobsMapping
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
from services.envision.helpers.task_distribution_system import task_distribution_system
from fastapi.encoders import jsonable_encoder
from database.rails_db import get_user



def create_air_freight_rate_jobs(request, source):
    updated_ids = []

    request = jsonable_encoder(request)
    for data in request:
        params = {
            'origin_airport_id' : data.get('origin_airport_id'),
            'destination_airport_id' : data.get('destination_airport_id'),
            'airline_id' : data.get('airline_id'),
            'service_provider_id' : data.get('service_provider_id'),
            'commodity' : data.get('commodity'),
            'source' : source,
            'rate_type' : data.get('rate_type'),
            'rate_id' : data.get('rate_id'),
            "commodity_type":data.get("commodity_type"),
            "commodity_sub_type":data.get("commodity_sub_type"),
            "stacking_type":data.get("stacking_type"),
            "shipment_type":data.get("shipment_type"),
            "operation_type":data.get("operation_type")
        }
        init_key = f'{str(params.get("origin_airport_id"))}:{str(params["destination_airport_id"] or "")}:{str(params["airline_id"])}:{str(params["service_provider_id"] or "")}:{str(params["commodity"])}:{str(params["source"])}:{str(params["rate_id"])}:{str(params["rate_type"])}:{str(params["commodity_type"] or "")}:{str(params["commodity_sub_type"] or "")}:{str(params["stacking_type"] or ""):{str(params["operation_type"] or "")}}'
        air_freight_rate_job = AirFreightRateJobs.select().where(init_key = init_key).first()
        params['init_key'] = init_key

        if not air_freight_rate_job:
            air_freight_rate_job = create_job_object(params)
        
        if air_freight_rate_job.status == 'active' or (air_freight_rate_job.status == 'inactive' and air_freight_rate_job.updated_at > (datetime.now()-timedelta(days=7))):
            continue

        if not air_freight_rate_job:
            air_freight_rate_job = AirFreightRateJobs()
            for key in list(params.keys()):
                setattr(air_freight_rate_job, key, params[key])
        if air_freight_rate_job.status == 'active':
            continue

        if air_freight_rate_job.status == 'inactive' and air_freight_rate_job.updated_at > datetime.now()-timedelta(days=7):
            continue

        user_id = task_distribution_system('AIR')
        air_freight_rate_job.assigned_to_id = user_id
        air_freight_rate_job.assigned_to = get_user(user_id)
        air_freight_rate_job.status = 'active'
        air_freight_rate_job.set_locations()
        air_freight_rate_job.save()
        set_jobs_mapping(air_freight_rate_job.id, data)
        get_multiple_service_objects(air_freight_rate_job)
        updated_ids.append(air_freight_rate_job.id)

    return {"updated_ids": updated_ids}

def set_jobs_mapping(jobs_id, data):
    audit_id = AirFreightRateJobsMapping.create(
        source_id=data.get("rate_id"),
        job_id= jobs_id,
        source = 'air_freight_rate'
    )
    return audit_id

def create_job_object(params):
    air_freight_rate_job = AirFreightRateJobs()
    for key in list(params.keys()):
        setattr(air_freight_rate_job, key, params[key])