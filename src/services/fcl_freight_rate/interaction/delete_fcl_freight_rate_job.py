from database.db_session import db
from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJobs
from services.fcl_freight_rate.models.fcl_freight_rate_jobs_mapping import FclFreightRateJobsMapping
from datetime import datetime
from fastapi import HTTPException

def delete_fcl_freight_rate_job(request):
    update_params = {'status':'inactive'}
    update_params['updated_at'] = datetime.now()
    fcl_freight_rate_job = FclFreightRateJobs.update(update_params).where(FclFreightRateJobs.id == request['id']).execute()
    set_jobs_mapping(request['id'], request)

    return {'id' : request['id']}


def set_jobs_mapping(jobs_id, data):
    audit_id = FclFreightRateJobsMapping.create(
        source_id=data.get("rate_id"),
        job_id= jobs_id,
        source = 'fcl_freight_rate',
        performed_by_id = data.get("performed_by_id")
    )
    return audit_id
