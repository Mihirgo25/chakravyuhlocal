from services.fcl_freight_rate.models.fcl_freight_rate_local_jobs import FclFreightRateLocalJob
from database.rails_db import get_user
from fastapi import HTTPException

def update_fcl_freight_rate_local_job(request):
    
    job_id = request.get('id')
    
    freight_rate_local_job = FclFreightRateLocalJob.select().where(FclFreightRateLocalJob.id == job_id).first()
    if not freight_rate_local_job:
        raise HTTPException(status_code=400, detail="Job ID does not exist")
    
    user_id = request.get('user_id')
    assigned_to =  get_user(user_id)[0]
    freight_rate_local_job.user_id = user_id
    freight_rate_local_job.assigned_to = assigned_to
    freight_rate_local_job.save()
    
    return { 'id': job_id }