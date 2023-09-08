from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJob
from datetime import datetime, timedelta

def update_fcl_freight_rate_jobs_to_backlog():
    
    fcl_conditions = (
        (FclFreightRateJob.created_at >= datetime.today().date() - timedelta(days=1)),
        (FclFreightRateJob.created_at < datetime.today().date()),
        (FclFreightRateJob.status == 'pending')
    )

    fcl_query = FclFreightRateJob.update(status='backlog').where(*fcl_conditions)
    fcl_query.execute()

