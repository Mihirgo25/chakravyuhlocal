from services.air_freight_rate.models.air_freight_rate_jobs import AirFreightRateJobs
from services.air_freight_rate.models.air_freight_rate_jobs_mapping import AirFreightRateJobsMapping
from database.rails_db import get_user


def update_air_freight_rate_job_on_rate_addition(request, id):
    update_params = {'status':'completed', "closed_by_id": request.get('performed_by_id'), "closed_by": get_user(request.get('performed_by_id'))[0]}
    origin_airport_id = request.get("origin_airport_id") or ""
    destination_airport_id = request.get("destination_airport_id") or ""
    commodity = request.get("commodity") or ""
    rate_type = request.get("rate_type") or ""
    commodity_type = request.get("commodity_type") or ""
    commodity_sub_type = request.get("commodity_sub_type") or ""
    stacking_type = request.get("stacking_type") or ""
    operation_type = request.get("operation_type") or ""

    airline_id_values = [request.get("airline_id") or "", ""]
    service_provider_id_values = [request.get("service_provider_id") or "", ""]
    
    possible_init_keys = []
    for airline_id in airline_id_values:
        for service_provider_id in service_provider_id_values:
            key = f"{origin_airport_id}:{destination_airport_id}:{airline_id}:{service_provider_id}:{commodity}:{rate_type}:{commodity_type}:{commodity_sub_type}:{stacking_type}:{operation_type}"
            possible_init_keys.append(key)
    air_freight_rate_job = AirFreightRateJobs.update(update_params).where(AirFreightRateJobs.init_key << possible_init_keys, AirFreightRateJobs.status << ['pending', 'backlog']).execute()
    set_jobs_mapping(air_freight_rate_job.id, request, id)

    return {'id' : request['id']}

def set_jobs_mapping(jobs_id, data, id):
    audit_id = AirFreightRateJobsMapping.create(
        source_id=id,
        job_id= jobs_id,
        performed_by_id = data.get("performed_by_id"),
        data = data.get('data')
    )
    return audit_id
