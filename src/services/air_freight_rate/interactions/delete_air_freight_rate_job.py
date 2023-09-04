from database.db_session import db
from services.air_freight_rate.models.air_freight_rate_jobs import AirFreightRateJobs
from services.air_freight_rate.models.air_freight_rate_jobs_mapping import AirFreightRateJobsMapping
from database.rails_db import get_user


POSSIBLE_CLOSING_REMARKS = ['not_serviceable', 'rate_not_available', 'no_change_in_rate']


def delete_air_freight_rate_job(request):
    if request.get('closing_remarks') and request.get('closing_remarks') in POSSIBLE_CLOSING_REMARKS:
        update_params = {'status':'aborted', "closed_by_id": request.get('performed_by_id'), "closed_by": get_user(request.get('performed_by_id'))[0]}
    else:
        update_params = {'status':'completed', "closed_by_id": request.get('performed_by_id'), "closed_by": get_user(request.get('performed_by_id'))[0]}

    air_freight_rate_job = AirFreightRateJobs.update(update_params).where(AirFreightRateJobs.id == request['id']).execute()
    set_jobs_mapping(request['id'], request)

    return {'id' : request['id']}


def set_jobs_mapping(jobs_id, data):
    audit_id = AirFreightRateJobsMapping.create(
        source_id=data.get("rate_id"),
        job_id= jobs_id,
        performed_by_id = data.get("performed_by_id"),
        data = data.get('data')
    )
    return audit_id
