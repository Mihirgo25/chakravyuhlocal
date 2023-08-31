from services.supply_tool.models.fcl_freight_rate_jobs import FclFreightRateJobs
from services.supply_tool.models.fcl_freight_rate_jobs_mapping import FclFreightRateJobsMapping
from datetime import datetime, timedelta
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
from services.supply_tool.helpers.task_distribution_system import task_distribution_system
from fastapi.encoders import jsonable_encoder


def create_fcl_freight_rate_jobs(request, source):
    updated_ids = []
    request = jsonable_encoder(request)
    for data in request:
        params = {
            'origin_port_id' : data.get('origin_port_id'),
            'origin_main_port_id' : data.get('origin_main_port_id'),
            'destination_port_id' : data.get('destination_port_id'),
            'destination_main_port_id' : data.get('destination_main_port_id'),
            'shipping_line_id' : data.get('shipping_line_id'),
            'service_provider_id' : data.get('service_provider_id'),
            'container_size' : data.get('container_size'),
            'container_type' : data.get('container_type'),
            'commodity' : data.get('commodity'),
            'source' : source,
            'rate_type' : data.get('rate_type'),
            'rate_id' : data.get('rate_id'),
        }
        conditions = [getattr(FclFreightRateJobs, key) == value for key, value in params.items() if value is not None]
        fcl_freight_rate_job = FclFreightRateJobs.select().where(*conditions).first()
        if not fcl_freight_rate_job:
            fcl_freight_rate_job = FclFreightRateJobs()
            for key in list(params.keys()):
                setattr(fcl_freight_rate_job, key, params[key])
        if fcl_freight_rate_job.status == 'active':
            continue

        if fcl_freight_rate_job.status == 'inactive' and fcl_freight_rate_job.updated_at > datetime.now()-timedelta(days=7):
            continue

        user_id = task_distribution_system('FCL')
        fcl_freight_rate_job.assigned_to_id = user_id
        fcl_freight_rate_job.status = 'active'
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


    