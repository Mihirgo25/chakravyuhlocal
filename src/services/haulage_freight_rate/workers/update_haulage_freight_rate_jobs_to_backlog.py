from services.haulage_freight_rate.models.haulage_freight_rate_jobs import (
    HaulageFreightRateJob,
)
from services.haulage_freight_rate.models.haulage_freight_rate_job_mappings import (
    HaulageFreightRateJobMapping,
)
from datetime import datetime, timedelta
from services.haulage_freight_rate.models.haulage_freight_rate_audit import (
    HaulageFreightRateAudit,
)
from fastapi.encoders import jsonable_encoder
from configs.env import DEFAULT_USER_ID

BATCH_SIZE = 100


def update_haulage_freight_rate_jobs_to_backlog():
    total_updated = 0
    total_affected_ids = []

    while True:
        haulage_conditions = (
            HaulageFreightRateJob.created_at
            < datetime.today().date() - timedelta(days=1),
            HaulageFreightRateJob.status == "pending",
            ~(HaulageFreightRateJob.sources.contains('live_booking') | HaulageFreightRateJob.sources.contains('rate_feedback') | HaulageFreightRateJob.sources.contains('rate_request'))
        )

        affected_ids = jsonable_encoder(
            [
                job.id
                for job in HaulageFreightRateJob.select(HaulageFreightRateJob.id)
                .where(*haulage_conditions)
                .limit(BATCH_SIZE)
            ]
        )
        if not affected_ids:
            break

        haulage_query = HaulageFreightRateJob.update(status="backlog").where(
            HaulageFreightRateJob.id.in_(affected_ids)
        )

        rows_updated = haulage_query.execute()

        HaulageFreightRateJobMapping.update(status="backlog").where(HaulageFreightRateJobMapping.job_id.in_(affected_ids)).execute()

        total_updated += rows_updated

        for affected_id in affected_ids:
            create_audit(affected_id)

        total_affected_ids.extend(affected_ids)

    return {"ids": total_affected_ids}


def create_audit(jobs_id):
    HaulageFreightRateAudit.create(
        action_name="update",
        object_id=jobs_id,
        object_type="HaulageFreightRateJob",
        performed_by_id=DEFAULT_USER_ID,
    )
