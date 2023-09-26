from services.fcl_customs_rate.models.fcl_customs_rate_jobs import FclCustomsRateJob
from datetime import datetime, timedelta

def update_fcl_customs_rate_jobs_to_backlog():

    fcl_conditions = (
        (FclCustomsRateJob.created_at >= datetime.today().date() - timedelta(days=1)),
        (FclCustomsRateJob.created_at < datetime.today().date()),
        (FclCustomsRateJob.status == 'pending')
    )

    fcl_query = FclCustomsRateJob.update(status='backlog').where(*fcl_conditions)
    fcl_query.execute()