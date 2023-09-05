from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJobs
from services.fcl_freight_rate.models.fcl_freight_rate_jobs_mapping import FclFreightRateJobsMapping
from database.rails_db import get_user


def update_fcl_freight_rate_job(request, id):
    update_params = {'status':'completed', "closed_by_id": request.get('performed_by_id'), "closed_by": get_user(request.get('performed_by_id'))[0]}
    init_key = f'{str(request.get("origin_port_id"))}:{str(request.get("destination_port_id") or "")}:{str(request.get("shipping_line_id"))}:{str(request.get("service_provider_id") or "")}:{str(request.get("container_size"))}:{str(request.get("container_type"))}:{str(request.get("commodity"))}:{str(request.get("rate_type"))}'
    fcl_freight_rate_job = FclFreightRateJobs.update(update_params).where(FclFreightRateJobs.init_key == init_key, FclFreightRateJobs.status << ['pending', 'backlog']).execute()
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
