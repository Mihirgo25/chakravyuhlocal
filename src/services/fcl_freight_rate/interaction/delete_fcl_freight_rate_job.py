from database.db_session import db
from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJobs
from services.fcl_freight_rate.models.fcl_freight_rate_jobs_mapping import FclFreightRateJobsMapping
from datetime import datetime
from fastapi import HTTPException

POSSIBLE_CLOSING_REMARKS = ['not_serviceable', 'rate_not_available', 'no_change_in_rate']


def delete_fcl_freight_rate_job(request):
    if request.get('closing_remarks') and request.get('closing_remarks') in POSSIBLE_CLOSING_REMARKS:
        update_params = {'status':'aborted'}
    else:
        update_params = {'status':'completed'}

    fcl_freight_rate_job = FclFreightRateJobs.update(update_params).where(FclFreightRateJobs.id == request['id']).execute()
    set_jobs_mapping(request['id'], request)

    return {'id' : request['id']}


def set_jobs_mapping(jobs_id, data):
    audit_id = FclFreightRateJobsMapping.create(
        source_id=data.get("rate_id"),
        job_id= jobs_id,
        closed_by_id = data.get("performed_by_id"),
        data = data.get('data')
    )
    return audit_id
