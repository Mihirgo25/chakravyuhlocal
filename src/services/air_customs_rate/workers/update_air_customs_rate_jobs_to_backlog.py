from services.air_customs_rate.models.air_customs_rate_jobs import AirCustomsRateJob
from services.air_customs_rate.models.air_customs_rate_job_mappings import AirCustomsRateJobMapping
from datetime import datetime, timedelta
from services.air_customs_rate.models.air_customs_rate_audit import AirCustomsRateAudit
from fastapi.encoders import jsonable_encoder
from configs.env import DEFAULT_USER_ID
BATCH_SIZE = 100


def update_air_customs_rate_jobs_to_backlog():
    total_updated = 0
    total_affected_ids = []

    while True:
        air_customs_conditions = (
            AirCustomsRateJob.created_at < datetime.today().date() - timedelta(days=1),
            AirCustomsRateJob.status == "pending",
            ~(AirCustomsRateJob.sources.contains('live_booking') | AirCustomsRateJob.sources.contains('rate_feedback') | AirCustomsRateJob.sources.contains('rate_request'))
        )
        
        affected_ids = jsonable_encoder([job.id for job in AirCustomsRateJob.select(AirCustomsRateJob.id).where(*air_customs_conditions).limit(BATCH_SIZE)])
        if not affected_ids:
            break  
        
        air_customs_query = (
            AirCustomsRateJob.update(status="backlog")
            .where(AirCustomsRateJob.id.in_(affected_ids))
        )
        
        rows_updated = air_customs_query.execute()

        AirCustomsRateJobMapping.update(status="backlog").where(AirCustomsRateJobMapping.job_id.in_(affected_ids)).execute()
                
        total_updated += rows_updated
        
        for affected_id in affected_ids:
            create_audit(affected_id)
        
        total_affected_ids.extend(affected_ids)

    return {"ids": total_affected_ids}

def create_audit(jobs_id):
    AirCustomsRateAudit.create(
        action_name="update",
        object_id=jobs_id,
        object_type="AirCustomsRateJob",
        performed_by_id=DEFAULT_USER_ID,
    )