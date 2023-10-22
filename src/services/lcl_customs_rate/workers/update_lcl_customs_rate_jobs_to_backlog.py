from services.lcl_customs_rate.models.lcl_customs_rate_jobs import LclCustomsRateJob
from services.lcl_customs_rate.models.lcl_customs_rate_job_mappings import (
    LclCustomsRateJobMapping,
)
from datetime import datetime, timedelta
from services.lcl_customs_rate.models.lcl_customs_rate_audit import LclCustomsRateAudit
from fastapi.encoders import jsonable_encoder
from configs.env import DEFAULT_USER_ID

BATCH_SIZE = 100


def update_lcl_customs_rate_jobs_to_backlog():
    total_updated = 0
    total_affected_ids = []

    while True:
        lcl_conditions = (
            LclCustomsRateJob.created_at < datetime.today().date() - timedelta(days=1),
            LclCustomsRateJob.status == "pending",
            ~(LclCustomsRateJob.sources.contains('live_booking') | LclCustomsRateJob.sources.contains('rate_feedback') | LclCustomsRateJob.sources.contains('rate_request'))
        )

        affected_ids = jsonable_encoder(
            [
                job.id
                for job in LclCustomsRateJob.select(LclCustomsRateJob.id)
                .where(*lcl_conditions)
                .limit(BATCH_SIZE)
            ]
        )
        if not affected_ids:
            break

        lcl_query = LclCustomsRateJob.update(status="backlog").where(
            LclCustomsRateJob.id.in_(affected_ids)
        )

        rows_updated = lcl_query.execute()

        LclCustomsRateJobMapping.update(status="backlog").where(LclCustomsRateJobMapping.job_id.in_(affected_ids)).execute()

        total_updated += rows_updated

        for affected_id in affected_ids:
            create_audit(affected_id)

        total_affected_ids.extend(affected_ids)

    return {"ids": total_affected_ids}


def create_audit(jobs_id):
    LclCustomsRateAudit.create(
        action_name="update",
        object_id=jobs_id,
        object_type="LclCustomsRateJob",
        performed_by_id=DEFAULT_USER_ID,
    )
