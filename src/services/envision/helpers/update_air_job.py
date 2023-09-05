from services.air_freight_rate.models.air_freight_rate_jobs import AirFreightRateJobs
from services.air_freight_rate.models.air_freight_rate_jobs_mapping import AirFreightRateJobsMapping
from database.rails_db import get_user


def update_air_job(request):
    update_params = {'status':'completed', "closed_by_id": request.get('performed_by_id'), "closed_by": get_user(request.get('performed_by_id'))[0]}
    init_key = f'{str(request.get("origin_airport_id"))}:{str(request.get("destination_airport_id") or "")}:{str(request.get("airline_id"))}:{str(request.get("service_provider_id") or "")}:{str(request.get("commodity"))}:{str(request.get("rate_id"))}:{str(request.get("rate_type"))}:{str(request.get("commodity_type") or "")}:{str(request.get("commodity_sub_type") or "")}:{str(request.get("stacking_type") or "")}:{str(request.get("operation_type") or "")}'
    air_freight_rate_job = AirFreightRateJobs.update(update_params).where(AirFreightRateJobs.init_key == init_key, AirFreightRateJobs.status << ['pending', 'backlog']).execute()
    set_jobs_mapping(air_freight_rate_job.id, request)

    return {'id' : request['id']}

def set_jobs_mapping(jobs_id, data):
    audit_id = AirFreightRateJobsMapping.create(
        source_id=data.get("rate_id"),
        job_id= jobs_id,
        performed_by_id = data.get("performed_by_id"),
        data = data.get('data')
    )
    return audit_id
