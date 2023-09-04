from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJobs
from services.air_freight_rate.models.air_freight_rate_jobs import AirFreightRateJobs
from datetime import datetime, timedelta

def update_jobs_status():
    
    fcl_conditions = (
        (FclFreightRateJobs.created_at >= datetime.today().date() - timedelta(days=1)),
        (FclFreightRateJobs.created_at < datetime.today().date()),
        (FclFreightRateJobs.status == 'pending')
    )

    air_conditions = (
        (AirFreightRateJobs.created_at >= datetime.today().date() - timedelta(days=1)),
        (AirFreightRateJobs.created_at < datetime.today().date()),
        (AirFreightRateJobs.status == 'pending')
    )

    fcl_query = FclFreightRateJobs.update(status='backlog').where(*fcl_conditions)
    air_query = AirFreightRateJobs.update(status='backlog').where(*air_conditions)
    fcl_query.execute()
    air_query.execute()

