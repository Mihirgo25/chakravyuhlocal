from database.db_session import db
from services.fcl_customs_rate.models.fcl_customs_rate_jobs import FclCustomsRateJob
from services.fcl_customs_rate.models.fcl_customs_rate_job_mappings import FclCustomsRateJobMapping
from database.rails_db import get_user
from datetime import datetime
from services.fcl_customs_rate.models.fcl_customs_rate_audit import FclCustomsRateAudit

POSSIBLE_CLOSING_REMARKS = ['not_serviceable', 'rate_not_available', 'no_change_in_rate']


def delete_fcl_customs_rate_job(request):
    if request.get('closing_remarks') and request.get('closing_remarks') in POSSIBLE_CLOSING_REMARKS:
        update_params = {'status':'aborted', "closed_by_id": request.get('performed_by_id'), "closed_by": get_user(request.get('performed_by_id'))[0], "updated_at": datetime.now(), "closing_remarks": request.get('closing_remarks')}
    else:
        update_params = {'status':'completed', "closed_by_id": request.get('performed_by_id'), "closed_by": get_user(request.get('performed_by_id'))[0], "updated_at": datetime.now()}

    if request.get('fcl_freight_rate_feedback_ids'):
        job_ids = [ str(job.job_id) for job in FclCustomsRateJobMapping.select(FclCustomsRateJobMapping.job_id).where(FclCustomsRateJobMapping.source_id << request['fcl_customs_rate_feedback_ids'])]
    elif request.get('fcl_freight_rate_request_ids'):
        job_ids = [ str(job.job_id) for job in FclCustomsRateJobMapping.select(FclCustomsRateJobMapping.job_id).where(FclCustomsRateJobMapping.source_id << request['fcl_customs_rate_request_ids'])]
    elif request.get("id"):
        job_ids = request.get("id")
    elif request.get("source_id"):
        job_ids = request.get('source_id')
    
    if not isinstance(job_ids, list):
        job_ids = [job_ids]
    
    fcl_freight_rate_job = FclCustomsRateJob.update(update_params).where(FclCustomsRateJob.id << job_ids, FclCustomsRateJob.status.not_in(['completed', 'aborted'])).execute()
    
    if fcl_freight_rate_job:
        create_audit(job_ids, request)

    return {"id": job_ids}


def create_audit(jobs_ids, data):
    for job_id in jobs_ids:
        FclCustomsRateAudit.create(
            action_name = 'delete',
            object_id = job_id,
            object_type = 'FclCustomsRateJob',
            data = data.get('data'),
            performed_by_id = data.get("performed_by_id")
        )