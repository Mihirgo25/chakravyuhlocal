from services.fcl_cfs_rate.models.fcl_cfs_rate_jobs import FclCfsRateJob
from database.rails_db import get_user
from fastapi import HTTPException

def update_fcl_cfs_rate_job(request):
    
    job_id = request.get('id')
    
    fcl_cfs_rate_job = FclCfsRateJob.select().where(FclCfsRateJob.id == job_id).first()
    if not fcl_cfs_rate_job:
        raise HTTPException(status_code=400, detail="Job ID does not exist")
    
    user_id = request.get('user_id')
    assigned_to =  get_user(user_id)[0]
    fcl_cfs_rate_job.user_id = user_id
    fcl_cfs_rate_job.assigned_to = assigned_to
    fcl_cfs_rate_job.save()
    
    return { 'id': job_id }