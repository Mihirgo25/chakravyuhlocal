from services.fcl_customs_rate.models.fcl_customs_rate_jobs import FclCustomsRateJob
from database.rails_db import get_user
from fastapi import HTTPException

def update_fcl_customs_rate_job(request):
    
    job_id = request.get('id')
    
    customs_job = FclCustomsRateJob.select().where(FclCustomsRateJob.id == job_id).first()
    if not customs_job:
        raise HTTPException(status_code=400, detail="Job ID does not exist")
    
    user_id = request.get('user_id')
    assigned_to =  get_user(user_id)[0]
    customs_job.user_id = user_id
    customs_job.assigned_to = assigned_to
    customs_job.save()
    
    return { 'id': job_id }