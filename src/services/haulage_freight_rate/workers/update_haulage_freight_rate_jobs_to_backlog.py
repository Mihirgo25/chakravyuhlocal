from services.haulage_freight_rate.models.haulage_freight_rate_jobs import HaulageFreightRateJob
from datetime import datetime, timedelta

def update_haulage_freight_rate_jobs_to_backlog():

    haulage_conditions = (
        (HaulageFreightRateJob.created_at >= datetime.today().date() - timedelta(days=1)),
        (HaulageFreightRateJob.created_at < datetime.today().date()),
        (HaulageFreightRateJob.status == 'pending')
    )

    haulage_query = HaulageFreightRateJob.update(status='backlog').where(*haulage_conditions)
    haulage_query.execute()