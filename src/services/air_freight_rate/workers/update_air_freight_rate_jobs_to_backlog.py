from services.air_freight_rate.models.air_freight_rate_jobs import AirFreightRateJob
from datetime import datetime, timedelta

def update_air_freight_rate_jobs_to_backlog():

    air_conditions = (
        (AirFreightRateJob.created_at >= datetime.today().date() - timedelta(days=1)),
        (AirFreightRateJob.created_at < datetime.today().date()),
        (AirFreightRateJob.status == 'pending')
    )

    air_query = AirFreightRateJob.update(status='backlog').where(*air_conditions)
    air_query.execute()

