from services.ltl_freight_rate.models.ltl_freight_rate_jobs import LtlFreightRateJob
from services.ltl_freight_rate.models.ltl_freight_rate_job_mappings import (
    LtlFreightRateJobMapping,
)
from datetime import datetime
from database.rails_db import get_user
from fastapi.encoders import jsonable_encoder
from services.ltl_freight_rate.models.ltl_freight_rate_audit import LtlFreightRateAudit




def update_ltl_freight_rate_job_on_rate_addition(request):
    update_params = {
        "status": "completed",
        "closed_by_id": request.get("performed_by_id"),
        "closed_by": get_user(request.get("performed_by_id"))[0],
        "updated_at": datetime.now()
    }

    params = {
        "origin_location_id": request.get("origin_location_id"),
        "destination_location_id": request.get("destination_location_id"),
        "transit_time": request.get("transit_time"),
        "commodity": request.get("commodity"),
        "density_factor": request.get("density_factor"),
    }
    conditions = [
        (getattr(LtlFreightRateJob, key) == value) for key, value in params.items()
    ]
    conditions.append(LtlFreightRateJob.status << ["pending", "backlog"])
    affected_ids = jsonable_encoder([
        job.id
        for job in LtlFreightRateJob.select(LtlFreightRateJob.id).where(*conditions)
    ])

    ltl_freight_rate_job = (
        LtlFreightRateJob.update(update_params).where(*conditions).execute()
    )
    if ltl_freight_rate_job:
        update_mapping(affected_ids)
        for affected_id in affected_ids:
            create_audit(affected_id, jsonable_encoder(request))
    return {"ids": affected_ids}

def update_mapping(jobs_ids):
    update_params = {'status': "completed",  "updated_at": datetime.now()}
    LtlFreightRateJobMapping.update(update_params).where(LtlFreightRateJobMapping.job_id << jobs_ids).execute()

def create_audit(jobs_id, data):
    LtlFreightRateAudit.create(
        action_name = 'delete',
        object_id = jobs_id,
        data = data,
        object_type = 'LtlFreightRateJob',
        performed_by_id=data.get("performed_by_id"),
    )
