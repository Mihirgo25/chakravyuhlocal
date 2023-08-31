from database.db_session import db
from services.supply_tool.models.air_freight_rate_jobs import AirFreightRateJobs
from services.supply_tool.models.air_freight_rate_jobs_mapping import AirFreightRateJobsMapping
from datetime import datetime
from fastapi import HTTPException

def delete_air_freight_rate_job(request):
    update_params = {'status':'inactive'}
    update_params['updated_at'] = datetime.now()
    air_freight_rate_job = AirFreightRateJobs.update(update_params).where(AirFreightRateJobs.id == request['id']).execute()
    set_jobs_mapping(request['id'], request)

    return {'id' : request['id']}


def set_jobs_mapping(jobs_id, data):
    audit_id = AirFreightRateJobsMapping.create(
        source_id=data.get("rate_id"),
        job_id= jobs_id,
        source = 'air_freight_rate',
        performed_by_id = data.get("performed_by_id")
    )
    return audit_id
