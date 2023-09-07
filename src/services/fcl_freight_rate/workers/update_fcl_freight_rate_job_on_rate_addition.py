from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJobs
from services.fcl_freight_rate.models.fcl_freight_rate_jobs_mapping import FclFreightRateJobsMapping
from database.rails_db import get_user

required_columns = ['origin_port_id', 'destination_port_id', 'container_size', 'container_type', 'commodity', 'rate_type']
dynamic_columns = ['shipping_line_id', 'service_provider_id']


def update_fcl_freight_rate_job_on_rate_addition(request, id):
    update_params = {'status':'completed', "closed_by_id": request.get('performed_by_id'), "closed_by": get_user(request.get('performed_by_id'))[0]}
    origin_port_id = request.get("origin_port_id")
    destination_port_id = request.get("destination_port_id") 
    container_size = request.get("container_size")
    container_type = request.get("container_type")
    commodity = request.get("commodity")
    rate_type = request.get("rate_type")

    shipping_line_values = [request.get("shipping_line_id"), ""]
    service_provider_values = [request.get("service_provider_id"), ""]
    
    possible_init_keys = []
    for shipping_line in shipping_line_values:
        for service_provider in service_provider_values:
            key = f"{origin_port_id}:{destination_port_id}:{shipping_line}:{service_provider}:{container_size}:{container_type}:{commodity}:{rate_type}"
            possible_init_keys.append(key)
    
    fcl_freight_rate_job = FclFreightRateJobs.update(update_params).where(FclFreightRateJobs.init_key << possible_init_keys, FclFreightRateJobs.status << ['pending', 'backlog']).execute()
    set_jobs_mapping(fcl_freight_rate_job.id, request, id)

    return {'id' : request['id']}

def set_jobs_mapping(jobs_id, data, id):
    audit_id = FclFreightRateJobsMapping.create(
        source_id=id,
        job_id= jobs_id,
        performed_by_id = data.get("performed_by_id"),
        data = data.get('data')
    )
    return audit_id
