from services.ltl_freight_rate.models.ltl_freight_rate_jobs import LtlFreightRateJob
from services.ltl_freight_rate.models.ltl_freight_rate_job_mappings import (
    LtlFreightRateJobMapping,
)
from datetime import datetime, timedelta
from services.ltl_freight_rate.models.ltl_freight_rate_audit import LtlFreightRateAudit
from fastapi.encoders import jsonable_encoder
from configs.env import DEFAULT_USER_ID

BATCH_SIZE = 100


def update_ltl_freight_rate_jobs_to_backlog():
    total_updated = 0
    total_affected_ids = []

    while True:
        ltl_conditions = (
            LtlFreightRateJob.created_at < datetime.today().date() - timedelta(days=1),
            LtlFreightRateJob.status == "pending",
            ~(LtlFreightRateJob.sources.contains('live_booking') | LtlFreightRateJob.sources.contains('rate_feedback') | LtlFreightRateJob.sources.contains('rate_request'))
        )

        affected_ids = jsonable_encoder(
            [
                job.id
                for job in LtlFreightRateJob.select(LtlFreightRateJob.id)
                .where(*ltl_conditions)
                .limit(BATCH_SIZE)
            ]
        )
        if not affected_ids:
            break

        ltl_query = LtlFreightRateJob.update(status="backlog").where(
            LtlFreightRateJob.id.in_(affected_ids)
        )

        rows_updated = ltl_query.execute()

        LtlFreightRateJobMapping.update(status="backlog").where(LtlFreightRateJobMapping.job_id.in_(affected_ids)).execute()

        total_updated += rows_updated

        for affected_id in affected_ids:
            create_audit(affected_id)

        total_affected_ids.extend(affected_ids)

    return {"ids": total_affected_ids}


def create_audit(jobs_id):
    LtlFreightRateAudit.create(
        action_name="update",
        object_id=jobs_id,
        object_type="LtlFreightRateJob",
        performed_by_id=DEFAULT_USER_ID,
    )
