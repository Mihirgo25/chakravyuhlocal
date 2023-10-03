from database.db_session import db
from services.air_freight_rate.models.air_freight_rate_local_jobs import (
    AirFreightRateLocalJob,
)
from services.air_freight_rate.models.air_freight_rate_local_jobs_mapping import (
    AirFreightRateLocalJobMapping,
)
from database.rails_db import get_user
from datetime import datetime
from services.air_freight_rate.models.air_services_audit import AirServiceAudit


POSSIBLE_CLOSING_REMARKS = [
    "not_serviceable",
    "rate_not_available",
    "no_change_in_rate",
]


def delete_air_freight_rate_local_job(request):
    if (
        request.get("closing_remarks")
        and request.get("closing_remarks") in POSSIBLE_CLOSING_REMARKS
    ):
        update_params = {
            "status": "aborted",
            "closed_by_id": request.get("performed_by_id"),
            "closed_by": get_user(request.get("performed_by_id"))[0],
            "updated_at": datetime.now(),
            "closing_remarks": request.get("closing_remarks"),
        }
    else:
        update_params = {
            "status": "completed",
            "closed_by_id": request.get("performed_by_id"),
            "closed_by": get_user(request.get("performed_by_id"))[0],
            "updated_at": datetime.now(),
        }

    air_freight_rate_job = (
        AirFreightRateLocalJob.update(update_params)
        .where(
            AirFreightRateLocalJob.id == request["id"],
            AirFreightRateLocalJob.status.not_in(["completed", "aborted"]),
        )
        .execute()
    )
    if air_freight_rate_job:
        update_mapping(update_params["status"], request["id"])
        create_audit(request["id"], request)

    return {"id": request["id"]}


def update_mapping(status, job_id):
    update_params = {"status": status, "updated_at": datetime.now()}
    AirFreightRateLocalJobMapping.update(update_params).where(
        (AirFreightRateLocalJobMapping.job_id == job_id)
        & (AirFreightRateLocalJobMapping.status.not_in(["completed", "aborted"]))
    ).execute()


def create_audit(job_id, data):
    AirServiceAudit.create(
        action_name="delete",
        object_id=job_id,
        object_type="AirFreightRateLocalJob",
        performed_by_id=data.get("performed_by_id"),
        data=data.get("data"),
    )
