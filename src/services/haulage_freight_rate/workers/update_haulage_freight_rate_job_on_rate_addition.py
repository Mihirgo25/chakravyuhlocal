from services.haulage_freight_rate.models.haulage_freight_rate_jobs import HaulageFreightRateJob
from services.haulage_freight_rate.models.haulage_freight_rate_job_mappings import (
    HaulageFreightRateJobMapping,
)
from datetime import datetime
from database.rails_db import get_user
from fastapi.encoders import jsonable_encoder
from services.haulage_freight_rate.models.haulage_freight_rate_audit import HaulageFreightRateAudit
from functools import reduce



def update_haulage_freight_rate_job_on_rate_addition(request, id):
    update_params = {
        "status": "completed",
        "closed_by_id": request.get("performed_by_id"),
        "closed_by": get_user(request.get("performed_by_id"))[0],
        "updated_at": datetime.now()
    }

    params = {
        "origin_location_id": request.get("origin_location_id"),
        "destination_location_id": request.get("destination_location_id"),
        "container_size": request.get("container_size"),
        "container_type": request.get("container_type"),
        "commodity": request.get("commodity"),
        "rate_type": request.get("rate_type"),
    }
    conditions = [
        (getattr(HaulageFreightRateJob, key) == value) for key, value in params.items()
    ]
    conditions.append(HaulageFreightRateJob.status << ["pending", "backlog"])
    exception_conditions = [(~HaulageFreightRateJob.sources.contains(tag)) for tag in ['live_booking','rate_request','rate_feedback']]
    combined_condition = reduce(lambda a, b: a & b, exception_conditions)
    conditions.append(combined_condition)
    affected_ids = jsonable_encoder([
        job.id
        for job in HaulageFreightRateJob.select(HaulageFreightRateJob.id).where(*conditions)
    ])

    haulage_freight_rate_job = (
        HaulageFreightRateJob.update(update_params).where(*conditions).execute()
    )
    if haulage_freight_rate_job:
        update_mapping(affected_ids)
        for affected_id in affected_ids:
            create_audit(affected_id, jsonable_encoder(request))
    return {"ids": affected_ids}

def update_mapping(jobs_ids):
    update_params = {'status': "completed",  "updated_at": datetime.now()}
    HaulageFreightRateJobMapping.update(update_params).where(HaulageFreightRateJobMapping.job_id << jobs_ids).execute()

def create_audit(jobs_id, data):
    HaulageFreightRateAudit.create(
        action_name = 'delete',
        object_id = jobs_id,
        data = data,
        object_type = 'HaulageFreightRateJob',
        performed_by_id=data.get("performed_by_id"),
    )