from services.air_freight_rate.models.air_freight_rate_jobs import AirFreightRateJob
from datetime import datetime, timedelta
from services.air_freight_rate.models.air_services_audit import AirServiceAudit
from fastapi.encoders import jsonable_encoder
from configs.env import DEFAULT_USER_ID
BATCH_SIZE = 100


def update_air_freight_rate_jobs_to_backlog():
    total_updated = 0
    total_affected_ids = []

    while True:
        air_conditions = (
            AirFreightRateJob.created_at < datetime.today().date() - timedelta(days=1),
            AirFreightRateJob.status == "pending"
        )

        affected_ids = jsonable_encoder([job.id for job in AirFreightRateJob.select(AirFreightRateJob.id).where(*air_conditions).limit(BATCH_SIZE)])
        
        if not affected_ids:
            break

        air_query = (
            AirFreightRateJob.update(status="backlog")
            .where(AirFreightRateJob.id.in_(affected_ids))
        )

        rows_updated = air_query.execute()

        total_updated += rows_updated

        for affected_id in affected_ids:
            create_audit(affected_id)

        total_affected_ids.extend(affected_ids)

    return {"ids": total_affected_ids}

def create_audit(jobs_id):
    AirServiceAudit.create(
        action_name="update",
        object_id=jobs_id,
        object_type="AirFreightRateJob",
        performed_by_id=DEFAULT_USER_ID,
    )