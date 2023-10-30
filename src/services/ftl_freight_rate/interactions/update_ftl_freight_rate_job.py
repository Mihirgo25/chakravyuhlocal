from services.ftl_freight_rate.models.ftl_freight_rate_jobs import FtlFreightRateJob
from database.rails_db import get_user
from fastapi import HTTPException

def update_ftl_freight_rate_job(request):
    
    job_id = request.get('id')
    
    freight_rate_job = FtlFreightRateJob.select().where(FtlFreightRateJob.id == job_id).first()
    if not freight_rate_job:
        raise HTTPException(status_code=400, detail="Job ID does not exist")
    
    user_id = request.get('user_id')
    assigned_to =  get_user(user_id)[0]
    freight_rate_job.user_id = user_id
    freight_rate_job.assigned_to = assigned_to
    freight_rate_job.save()
    
    return { 'id': job_id }