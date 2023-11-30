from services.fcl_cfs_rate.models.fcl_cfs_rate_jobs import FclCfsRateJob
from services.fcl_cfs_rate.models.fcl_cfs_rate_job_mappings import (
    FclCfsRateJobMapping,
)
from datetime import datetime
from database.rails_db import get_user
from fastapi.encoders import jsonable_encoder
from services.fcl_cfs_rate.models.fcl_cfs_rate_audit import FclCfsRateAudit
from functools import reduce



def update_fcl_cfs_rate_job_on_rate_addition(request, id):
    update_params = {
        "status": "completed",
        "closed_by_id": request.get("performed_by_id"),
        "closed_by": get_user(request.get("performed_by_id"))[0],
        "updated_at": datetime.now()
    }

    params = {
        "location_id": request.get("location_id"),
        "trade_type": request.get("trade_type"),
        "container_size": request.get("container_size"),
        "container_type": request.get("container_type"),
        "commodity": request.get("commodity"),
        "rate_type": request.get("rate_type"),
    }
    conditions = [
        (getattr(FclCfsRateJob, key) == value) for key, value in params.items()
    ]
    conditions.append(FclCfsRateJob.status << ["pending", "backlog"])
    exception_conditions = [(~FclCfsRateJob.sources.contains(tag)) for tag in ['live_booking','rate_request','rate_feedback']]
    combined_condition = reduce(lambda a, b: a & b, exception_conditions)
    conditions.append(combined_condition)
    affected_ids = jsonable_encoder([
        job.id
        for job in FclCfsRateJob.select(FclCfsRateJob.id).where(*conditions)
    ])

    fcl_cfs_rate_job = (
        FclCfsRateJob.update(update_params).where(*conditions).execute()
    )
    if fcl_cfs_rate_job:
        update_mapping(affected_ids)
        for affected_id in affected_ids:
            create_audit(affected_id, jsonable_encoder(request))
    return {"ids": affected_ids}

def update_mapping(jobs_ids):
    update_params = {'status': "completed",  "updated_at": datetime.now()}
    FclCfsRateJobMapping.update(update_params).where(FclCfsRateJobMapping.job_id << jobs_ids).execute()

def create_audit(jobs_id, data):
    FclCfsRateAudit.create(
        action_name = 'delete',
        object_id = jobs_id,
        data = data,
        object_type = 'FclCfsRateJob',
        performed_by_id=data.get("performed_by_id"),
    )
