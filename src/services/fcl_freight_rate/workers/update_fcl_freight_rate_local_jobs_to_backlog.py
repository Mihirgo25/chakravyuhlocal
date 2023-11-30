from services.fcl_freight_rate.models.fcl_freight_rate_local_job import FclFreightRateLocalJob
from services.fcl_freight_rate.models.fcl_freight_rate_local_job_mapping import FclFreightRateLocalJobMapping
from datetime import datetime
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
from fastapi.encoders import jsonable_encoder
from configs.env import DEFAULT_USER_ID
BATCH_SIZE = 100


def update_fcl_freight_rate_local_jobs_to_backlog():
    total_updated = 0
    total_affected_ids = []

    while True:
        fcl_conditions = (
            FclFreightRateLocalJob.created_at <= datetime.today().date(),
            FclFreightRateLocalJob.status == "pending",
            ~(FclFreightRateLocalJob.sources.contains('live_booking') | FclFreightRateLocalJob.sources.contains('rate_feedback') | FclFreightRateLocalJob.sources.contains('rate_request'))
        )
        
        affected_ids = jsonable_encoder([job.id for job in FclFreightRateLocalJob.select(FclFreightRateLocalJob.id).where(*fcl_conditions).limit(BATCH_SIZE)])
        if not affected_ids:
            break  
        
        fcl_query = (
            FclFreightRateLocalJob.update(status="backlog")
            .where(FclFreightRateLocalJob.id.in_(affected_ids))
        )
        
        rows_updated = fcl_query.execute()

        FclFreightRateLocalJobMapping.update(status="backlog").where(FclFreightRateLocalJobMapping.job_id.in_(affected_ids)).execute()
                
        total_updated += rows_updated
        
        for affected_id in affected_ids:
            create_audit(affected_id)
        
        total_affected_ids.extend(affected_ids)

    return {"ids": total_affected_ids}

def create_audit(jobs_id):
    FclServiceAudit.create(
        action_name="update",
        object_id=jobs_id,
        object_type="FclFreightRateLocalJob",
        performed_by_id=DEFAULT_USER_ID,
    )
