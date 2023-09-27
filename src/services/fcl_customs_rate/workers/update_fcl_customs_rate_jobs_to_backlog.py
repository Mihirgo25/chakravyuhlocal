from services.fcl_customs_rate.models.fcl_customs_rate_jobs import FclCustomsRateJob
from datetime import datetime, timedelta
from services.fcl_customs_rate.models.fcl_customs_rate_audit import FclCustomsRateAudit
from fastapi.encoders import jsonable_encoder
from configs.env import DEFAULT_USER_ID
BATCH_SIZE = 100


def update_fcl_customs_rate_jobs_to_backlog():
    total_updated = 0
    total_affected_ids = []

    while True:
        haulage_conditions = (
            FclCustomsRateJob.created_at < datetime.today().date() - timedelta(days=1),
            FclCustomsRateJob.status == "pending",
        )
        
        affected_ids = jsonable_encoder([job.id for job in FclCustomsRateJob.select(FclCustomsRateJob.id).where(*haulage_conditions).limit(BATCH_SIZE)])
        if not affected_ids:
            break  
        
        haulage_query = (
            FclCustomsRateJob.update(status="backlog")
            .where(FclCustomsRateJob.id.in_(affected_ids))
        )
        
        rows_updated = haulage_query.execute()
        
        total_updated += rows_updated
        
        for affected_id in affected_ids:
            create_audit(affected_id)
        
        total_affected_ids.extend(affected_ids)

    return {"ids": total_affected_ids}

def create_audit(jobs_id):
    FclCustomsRateAudit.create(
        action_name="update",
        object_id=jobs_id,
        object_type="FclCustomsRateJob",
        performed_by_id=DEFAULT_USER_ID,
    )