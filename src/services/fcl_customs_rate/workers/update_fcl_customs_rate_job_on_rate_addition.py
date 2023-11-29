from services.fcl_customs_rate.models.fcl_customs_rate_jobs import FclCustomsRateJob
from services.fcl_customs_rate.models.fcl_customs_rate_job_mappings import (
    FclCustomsRateJobMapping,
)
from datetime import datetime
from database.rails_db import get_user
from fastapi.encoders import jsonable_encoder
from services.fcl_customs_rate.models.fcl_customs_rate_audit import FclCustomsRateAudit
from functools import reduce



def update_fcl_customs_rate_job_on_rate_addition(request, id):
    update_params = {
        "status": "completed",
        "closed_by_id": request.get("performed_by_id"),
        "closed_by": get_user(request.get("performed_by_id"))[0],
        "updated_at": datetime.now()
    }

    params = {
        "location_id": request.get("location_id"),
        "container_size": request.get("container_size"),
        "container_type": request.get("container_type"),
        "commodity": request.get("commodity"),
        "rate_type": request.get("rate_type"),
        "trade_type": request.get("trade_type"),
        "cargo_handling_type": request.get("cargo_handling_type")
    }
    conditions = [
        (getattr(FclCustomsRateJob, key) == value) for key, value in params.items()
    ]
    conditions.append(FclCustomsRateJob.status << ["pending", "backlog"])
    exception_conditions = [(~FclCustomsRateJob.sources.contains(tag)) for tag in ['live_booking','rate_request','rate_feedback']]
    combined_condition = reduce(lambda a, b: a & b, exception_conditions)
    conditions.append(combined_condition)
    affected_ids = jsonable_encoder([
        job.id
        for job in FclCustomsRateJob.select(FclCustomsRateJob.id).where(*conditions)
    ])

    fcl_customs_rate_job = (
        FclCustomsRateJob.update(update_params).where(*conditions).execute()
    )
    if fcl_customs_rate_job:
        update_mapping(affected_ids)
        for affected_id in affected_ids:
            create_audit(affected_id, jsonable_encoder(request))
    return {"ids": affected_ids}

def update_mapping(jobs_ids):
    update_params = {'status': "completed",  "updated_at": datetime.now()}
    FclCustomsRateJobMapping.update(update_params).where(FclCustomsRateJobMapping.job_id << jobs_ids).execute()

def create_audit(jobs_id, data):
    FclCustomsRateAudit.create(
        action_name = 'delete',
        object_id = jobs_id,
        data = data,
        object_type = 'FclCustomsRateJob',
        performed_by_id=data.get("performed_by_id"),
    )