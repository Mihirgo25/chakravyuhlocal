from services.lcl_customs_rate.models.lcl_customs_rate_jobs import LclCustomsRateJob
from services.lcl_customs_rate.models.lcl_customs_rate_job_mappings import (
    LclCustomsRateJobMapping,
)
from datetime import datetime
from database.rails_db import get_user
from fastapi.encoders import jsonable_encoder
from services.lcl_customs_rate.models.lcl_customs_rate_audit import LclCustomsRateAudit




def update_lcl_customs_rate_job_on_rate_addition(request):
    update_params = {
        "status": "completed",
        "closed_by_id": request.get("performed_by_id"),
        "closed_by": get_user(request.get("performed_by_id"))[0],
        "updated_at": datetime.now()
    }

    params = {
        "location_id": request.get("location_id"),
        "trade_type": request.get("trade_type"),
        "commodity": request.get("commodity"),
        "container_size": request.get("container_size"),
        "container_type": request.get("container_type"),
        "rate_type": request.get("rate_type"),
    }
    conditions = [
        (getattr(LclCustomsRateJob, key) == value) for key, value in params.items()
    ]
    conditions.append(LclCustomsRateJob.status << ["pending", "backlog"])
    affected_ids = jsonable_encoder([
        job.id
        for job in LclCustomsRateJob.select(LclCustomsRateJob.id).where(*conditions)
    ])

    lcl_customs_rate_job = (
        LclCustomsRateJob.update(update_params).where(*conditions).execute()
    )
    if lcl_customs_rate_job:
        update_mapping(affected_ids)
        for affected_id in affected_ids:
            create_audit(affected_id, jsonable_encoder(request))
    return {"ids": affected_ids}

def update_mapping(jobs_ids):
    update_params = {'status': "completed",  "updated_at": datetime.now()}
    LclCustomsRateJobMapping.update(update_params).where(LclCustomsRateJobMapping.job_id << jobs_ids).execute()

def create_audit(jobs_id, data):
    LclCustomsRateAudit.create(
        action_name = 'delete',
        object_id = jobs_id,
        data = data,
        object_type = 'LclCustomsRateJob',
        performed_by_id=data.get("performed_by_id"),
    )
