from services.ftl_freight_rate.models.ftl_freight_rate_jobs import FtlFreightRateJob
from services.ftl_freight_rate.models.ftl_freight_rate_job_mappings import (
    FtlFreightRateJobMapping,
)
from datetime import datetime, timedelta
from services.ftl_freight_rate.models.ftl_freight_rate_audit import FtlFreightRateAudit
from fastapi.encoders import jsonable_encoder
from configs.env import DEFAULT_USER_ID

BATCH_SIZE = 100


def update_ftl_freight_rate_jobs_to_backlog():
    total_updated = 0
    total_affected_ids = []

    while True:
        ftl_conditions = (
            FtlFreightRateJob.created_at < datetime.today().date() - timedelta(days=1),
            FtlFreightRateJob.status == "pending",
            ~(FtlFreightRateJob.sources.contains('live_booking') | FtlFreightRateJob.sources.contains('rate_feedback') | FtlFreightRateJob.sources.contains('rate_request'))
        )

        affected_ids = jsonable_encoder(
            [
                job.id
                for job in FtlFreightRateJob.select(FtlFreightRateJob.id)
                .where(*ftl_conditions)
                .limit(BATCH_SIZE)
            ]
        )
        if not affected_ids:
            break

        ftl_query = FtlFreightRateJob.update(status="backlog").where(
            FtlFreightRateJob.id.in_(affected_ids)
        )

        rows_updated = ftl_query.execute()

        FtlFreightRateJobMapping.update(status="backlog").where(
            FtlFreightRateJobMapping.job_id.in_(affected_ids)
        ).execute()

        total_updated += rows_updated

        for affected_id in affected_ids:
            create_audit(affected_id)

        total_affected_ids.extend(affected_ids)

    return {"ids": total_affected_ids}


def create_audit(jobs_id):
    FtlFreightRateAudit.create(
        action_name="update",
        object_id=jobs_id,
        object_type="FtlFreightRateJob",
        performed_by_id=DEFAULT_USER_ID,
    )
