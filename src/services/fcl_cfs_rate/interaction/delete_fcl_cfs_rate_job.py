from database.db_session import db
from services.fcl_cfs_rate.models.fcl_cfs_rate_jobs import FclCfsRateJob
from services.fcl_cfs_rate.models.fcl_cfs_rate_job_mappings import FclCfsRateJobMapping
from database.rails_db import get_user
from datetime import datetime
from services.fcl_cfs_rate.models.fcl_cfs_rate_audit import FclCfsRateAudit


POSSIBLE_CLOSING_REMARKS = ['not_serviceable', 'rate_not_available', 'no_change_in_rate']


def delete_fcl_cfs_rate_job(request):

    if request.get('closing_remarks') and request.get('closing_remarks') in POSSIBLE_CLOSING_REMARKS:
        update_params = {'status':'aborted', "closed_by_id": request.get('performed_by_id'), "closed_by": get_user(request.get('performed_by_id'))[0], "updated_at": datetime.now(),  "closing_remarks": request.get('closing_remarks')}
    else:
        update_params = {'status':'completed', "closed_by_id": request.get('performed_by_id'), "closed_by": get_user(request.get('performed_by_id'))[0], "updated_at": datetime.now()}
    
    if request.get('fcl_cfs_rate_feedback_ids'):
        job_ids = [ str(job.job_id) for job in FclCfsRateJobMapping.select(FclCfsRateJobMapping.job_id).where(FclCfsRateJobMapping.source_id << request['fcl_cfs_rate_feedback_ids'])]
    elif request.get('fcl_cfs_rate_request_ids'):
        job_ids = [ str(job.job_id) for job in FclCfsRateJobMapping.select(FclCfsRateJobMapping.job_id).where(FclCfsRateJobMapping.source_id << request['fcl_cfs_rate_request_ids'])]
    else:
        job_ids = request.get('id')

    if not isinstance(job_ids, list):
        job_ids = [job_ids]

    fcl_cfs_rate_job = FclCfsRateJob.update(update_params).where(FclCfsRateJob.id << job_ids, FclCfsRateJob.status.not_in(['completed', 'aborted'])).execute()

    if fcl_cfs_rate_job:
        update_mapping(update_params['status'], job_ids)
        create_audit(job_ids, request)

    return {'id' : job_ids}


def create_audit(jobs_ids, data):
    for job_id in jobs_ids:
        FclCfsRateAudit.create(
            action_name = 'delete',
            object_id = job_id,
            object_type = 'FclCfsRateJob',
            performed_by_id = data.get("performed_by_id"),
            data = data.get('data')
        )
        
def update_mapping(status, job_ids):
    update_params = {'status':status, "updated_at": datetime.now()}
    FclCfsRateJobMapping.update(update_params).where(FclCfsRateJobMapping.job_id << job_ids, FclCfsRateJobMapping.status.not_in(['completed', 'aborted'])).execute()