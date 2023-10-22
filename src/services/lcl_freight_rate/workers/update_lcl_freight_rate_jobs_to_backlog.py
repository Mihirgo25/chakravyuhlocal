from services.lcl_freight_rate.models.lcl_freight_rate_jobs import LclFreightRateJob
from services.lcl_freight_rate.models.lcl_freight_rate_job_mappings import (
    LclFreightRateJobMapping,
)
from datetime import datetime, timedelta
from services.lcl_freight_rate.models.lcl_freight_rate_audit import LclFreightRateAudit
from fastapi.encoders import jsonable_encoder
from configs.env import DEFAULT_USER_ID

BATCH_SIZE = 100


def update_lcl_freight_rate_jobs_to_backlog():
    total_updated = 0
    total_affected_ids = []

    while True:
        lcl_conditions = (
            LclFreightRateJob.created_at < datetime.today().date() - timedelta(days=1),
            LclFreightRateJob.status == "pending",
            ~(LclFreightRateJob.sources.contains('live_booking') | LclFreightRateJob.sources.contains('rate_feedback') | LclFreightRateJob.sources.contains('rate_request'))
        )

        affected_ids = jsonable_encoder(
            [
                job.id
                for job in LclFreightRateJob.select(LclFreightRateJob.id)
                .where(*lcl_conditions)
                .limit(BATCH_SIZE)
            ]
        )
        if not affected_ids:
            break

        lcl_query = LclFreightRateJob.update(status="backlog").where(
            LclFreightRateJob.id.in_(affected_ids)
        )

        rows_updated = lcl_query.execute()

        LclFreightRateJobMapping.update(status="backlog").where(LclFreightRateJobMapping.job_id.in_(affected_ids)).execute()

        total_updated += rows_updated

        for affected_id in affected_ids:
            create_audit(affected_id)

        total_affected_ids.extend(affected_ids)

    return {"ids": total_affected_ids}


def create_audit(jobs_id):
    LclFreightRateAudit.create(
        action_name="update",
        object_id=jobs_id,
        object_type="LclFreightRateJob",
        performed_by_id=DEFAULT_USER_ID,
    )
