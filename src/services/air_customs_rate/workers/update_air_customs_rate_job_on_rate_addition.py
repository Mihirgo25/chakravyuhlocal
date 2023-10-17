from services.air_customs_rate.models.air_customs_rate_jobs import AirCustomsRateJob
from services.air_customs_rate.models.air_customs_rate_job_mappings import (
    AirCustomsRateJobMapping,
)
from datetime import datetime
from database.rails_db import get_user
from fastapi.encoders import jsonable_encoder
from services.air_customs_rate.models.air_customs_rate_audit import AirCustomsRateAudit




def update_air_customs_rate_job_on_rate_addition(request, id):
    update_params = {
        "status": "completed",
        "closed_by_id": request.get("performed_by_id"),
        "closed_by": get_user(request.get("performed_by_id"))[0],
        "updated_at": datetime.now()
    }

    params = {
        "airport_id": request.get("airport_id"),
        "commodity": request.get("commodity"),
        "rate_type": request.get("rate_type"),
        "commodity_type": request.get("commodity_type"),
        "commodity_sub_type": request.get("commodity_sub_type"),
        "stacking_type": request.get("stacking_type"),
        "operation_type": request.get("operation_type"),
    }
    conditions = [
        (getattr(AirCustomsRateJob, key) == value) for key, value in params.items()
    ]
    conditions.append(AirCustomsRateJob.status << ["pending", "backlog"])
    affected_ids = jsonable_encoder([
        job.id
        for job in AirCustomsRateJob.select(AirCustomsRateJob.id).where(*conditions)
    ])

    air_customs_rate_job = (
        AirCustomsRateJob.update(update_params).where(*conditions).execute()
    )
    if air_customs_rate_job:
        update_mapping(affected_ids)
        for affected_id in affected_ids:
            create_audit(affected_id, jsonable_encoder(request))
    return {"ids": affected_ids}

def update_mapping(jobs_ids):
    update_params = {'status': "completed",  "updated_at": datetime.now()}
    AirCustomsRateJobMapping.update(update_params).where(AirCustomsRateJobMapping.job_id << jobs_ids).execute()

def create_audit(jobs_id, data):
    AirCustomsRateAudit.create(
        action_name = 'delete',
        object_id = jobs_id,
        data = data,
        object_type = 'AirCustomsRateJob',
        performed_by_id=data.get("performed_by_id"),
    )