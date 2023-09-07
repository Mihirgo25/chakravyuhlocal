from services.air_freight_rate.models.air_freight_rate_jobs import AirFreightRateJobs
from datetime import datetime, timedelta

def update_air_freight_rate_jobs_to_backlog():

    air_conditions = (
        (AirFreightRateJobs.created_at >= datetime.today().date() - timedelta(days=1)),
        (AirFreightRateJobs.created_at < datetime.today().date()),
        (AirFreightRateJobs.status == 'pending')
    )

    air_query = AirFreightRateJobs.update(status='backlog').where(*air_conditions)
    air_query.execute()

