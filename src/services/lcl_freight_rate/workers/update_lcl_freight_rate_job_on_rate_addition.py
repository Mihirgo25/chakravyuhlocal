from services.lcl_freight_rate.models.lcl_freight_rate_jobs import LclFreightRateJob
from services.lcl_freight_rate.models.lcl_freight_rate_job_mappings import (
    LclFreightRateJobMapping,
)
from datetime import datetime
from database.rails_db import get_user
from fastapi.encoders import jsonable_encoder
from services.lcl_freight_rate.models.lcl_freight_rate_audit import LclFreightRateAudit




def update_lcl_freight_rate_job_on_rate_addition(request):
    update_params = {
        "status": "completed",
        "closed_by_id": request.get("performed_by_id"),
        "closed_by": get_user(request.get("performed_by_id"))[0],
        "updated_at": datetime.now()
    }

    params = {
        "origin_port_id": request.get("origin_port_id"),
        "destination_port_id": request.get("destination_port_id"),
        "commodity": request.get("commodity"),
        "rate_type": request.get("rate_type"),
    }
    conditions = [
        (getattr(LclFreightRateJob, key) == value) for key, value in params.items()
    ]
    conditions.append(LclFreightRateJob.status << ["pending", "backlog"])
    conditions.append(~(LclFreightRateJob.sources.contains('live_booking')))
    affected_ids = jsonable_encoder([
        job.id
        for job in LclFreightRateJob.select(LclFreightRateJob.id).where(*conditions)
    ])

    lcl_freight_rate_job = (
        LclFreightRateJob.update(update_params).where(*conditions).execute()
    )
    if lcl_freight_rate_job:
        update_mapping(affected_ids)
        for affected_id in affected_ids:
            create_audit(affected_id, jsonable_encoder(request))
    return {"ids": affected_ids}

def update_mapping(jobs_ids):
    update_params = {'status': "completed",  "updated_at": datetime.now()}
    LclFreightRateJobMapping.update(update_params).where(LclFreightRateJobMapping.job_id << jobs_ids).execute()

def create_audit(jobs_id, data):
    LclFreightRateAudit.create(
        action_name = 'delete',
        object_id = jobs_id,
        data = data,
        object_type = 'LclFreightRateJob',
        performed_by_id=data.get("performed_by_id"),
    )
