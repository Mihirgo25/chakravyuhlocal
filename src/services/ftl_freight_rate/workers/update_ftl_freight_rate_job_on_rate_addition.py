from services.ftl_freight_rate.models.ftl_freight_rate_jobs import FtlFreightRateJob
from services.ftl_freight_rate.models.ftl_freight_rate_job_mappings import (
    FtlFreightRateJobMapping,
)
from datetime import datetime
from database.rails_db import get_user
from fastapi.encoders import jsonable_encoder
from services.ftl_freight_rate.models.ftl_freight_rate_audit import FtlFreightRateAudit




def update_ftl_freight_rate_job_on_rate_addition(request, id):
    update_params = {
        "status": "completed",
        "closed_by_id": request.get("performed_by_id"),
        "closed_by": get_user(request.get("performed_by_id"))[0],
        "updated_at": datetime.now()
    }

    params = {
        "origin_location_id": request.get("origin_location_id"),
        "destination_location_id": request.get("destination_location_id"),
        "trip_type": request.get("trip_type"),
        "truck_type": request.get("truck_type"),
        "truck_body_type": request.get("truck_body_type"),
        "commodity": request.get("commodity"),
        "rate_type": request.get("rate_type"),
    }
    conditions = [
        (getattr(FtlFreightRateJob, key) == value) for key, value in params.items()
    ]
    conditions.append(FtlFreightRateJob.status << ["pending", "backlog"])
    conditions.append(~(FtlFreightRateJob.sources.contains('live_booking')))

    affected_ids = jsonable_encoder([
        job.id
        for job in FtlFreightRateJob.select(FtlFreightRateJob.id).where(*conditions)
    ])

    ftl_freight_rate_job = (
        FtlFreightRateJob.update(update_params).where(*conditions).execute()
    )
    if ftl_freight_rate_job:
        update_mapping(affected_ids)
        for affected_id in affected_ids:
            create_audit(affected_id, jsonable_encoder(request))
    return {"ids": affected_ids}

def update_mapping(jobs_ids):
    update_params = {'status': "completed",  "updated_at": datetime.now()}
    FtlFreightRateJobMapping.update(update_params).where(FtlFreightRateJobMapping.job_id << jobs_ids).execute()

def create_audit(jobs_id, data):
    FtlFreightRateAudit.create(
        action_name = 'delete',
        object_id = jobs_id,
        data = data,
        object_type = 'FtlFreightRateJob',
        performed_by_id=data.get("performed_by_id"),
    )
