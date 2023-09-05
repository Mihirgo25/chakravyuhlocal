from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJobs
from datetime import datetime, timedelta

def update_fcl_freight_job_status():
    
    fcl_conditions = (
        (FclFreightRateJobs.created_at >= datetime.today().date() - timedelta(days=1)),
        (FclFreightRateJobs.created_at < datetime.today().date()),
        (FclFreightRateJobs.status == 'pending')
    )

    fcl_query = FclFreightRateJobs.update(status='backlog').where(*fcl_conditions)
    fcl_query.execute()

