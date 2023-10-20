from services.fcl_cfs_rate.models.fcl_cfs_rate_jobs import FclCfsRateJob
from services.fcl_cfs_rate.models.fcl_cfs_rate_job_mappings import FclCfsRateJobMapping
from datetime import datetime, timedelta
from services.fcl_cfs_rate.models.fcl_cfs_rate_audit import FclCfsRateAudit
from fastapi.encoders import jsonable_encoder
from configs.env import DEFAULT_USER_ID
BATCH_SIZE = 100


def update_fcl_cfs_rate_jobs_to_backlog():
    total_updated = 0
    total_affected_ids = []

    while True:
        fcl_conditions = (
            FclCfsRateJob.created_at < datetime.today().date() - timedelta(days=1),
            FclCfsRateJob.status == "pending",
            ~(FclCfsRateJob.sources.contains('live_booking') | FclCfsRateJob.sources.contains('rate_feedback') | FclCfsRateJob.sources.contains('rate_request'))
        )
        
        affected_ids = jsonable_encoder([job.id for job in FclCfsRateJob.select(FclCfsRateJob.id).where(*fcl_conditions).limit(BATCH_SIZE)])
        if not affected_ids:
            break  
        
        fcl_query = (
            FclCfsRateJob.update(status="backlog")
            .where(FclCfsRateJob.id.in_(affected_ids))
        )
        
        rows_updated = fcl_query.execute()
        
        FclCfsRateJobMapping.update(status="backlog").where(FclCfsRateJobMapping.job_id.in_(affected_ids)).execute()
        
        total_updated += rows_updated
        
        for affected_id in affected_ids:
            create_audit(affected_id)
        
        total_affected_ids.extend(affected_ids)

    return {"ids": total_affected_ids}

def create_audit(jobs_id):
    FclCfsRateAudit.create(
        action_name="update",
        object_id=jobs_id,
        object_type="FclCfsRateJob",
        performed_by_id=DEFAULT_USER_ID,
    )
