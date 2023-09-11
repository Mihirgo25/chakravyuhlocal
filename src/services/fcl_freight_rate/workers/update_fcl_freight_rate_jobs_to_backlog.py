from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJob
from datetime import datetime, timedelta
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
from fastapi.encoders import jsonable_encoder
from configs.env import DEFAULT_USER_ID
BATCH_SIZE = 100


def update_fcl_freight_rate_jobs_to_backlog():
    total_updated = 0
    total_affected_ids = []

    while True:
        fcl_conditions = (
            FclFreightRateJob.created_at < datetime.today().date() - timedelta(days=1),
            FclFreightRateJob.status == "pending",
        )
        
        affected_ids = jsonable_encoder([job.id for job in FclFreightRateJob.select(FclFreightRateJob.id).where(*fcl_conditions).limit(BATCH_SIZE)])
        if not affected_ids:
            break  # No more records to update
        
        # Update records to "backlog"
        fcl_query = (
            FclFreightRateJob.update(status="backlog")
            .where(FclFreightRateJob.id.in_(affected_ids))
        )
        
        rows_updated = fcl_query.execute()
        
        total_updated += rows_updated
        
        # Create audit for affected_ids
        for affected_id in affected_ids:
            create_audit(affected_id)
        
        total_affected_ids.extend(affected_ids)

    return {"ids": total_affected_ids}

def create_audit(jobs_id):
    FclServiceAudit.create(
        action_name="update",
        object_id=jobs_id,
        object_type="FclFreightRateJob",
        performed_by_id=DEFAULT_USER_ID,
    )
