from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJob
from services.fcl_freight_rate.models.fcl_freight_rate_job_mappings import (
    FclFreightRateJobMapping,
)
from datetime import datetime
from database.rails_db import get_user
from fastapi.encoders import jsonable_encoder



def update_fcl_freight_rate_job_on_rate_addition(request, id):
    update_params = {
        "status": "completed",
        "closed_by_id": request.get("performed_by_id"),
        "closed_by": get_user(request.get("performed_by_id"))[0],
        "updated_at": datetime.now()
    }

    params = {
        "origin_port_id": request.get("origin_port_id"),
        "origin_main_port_id": request.get("origin_main_port_id"),
        "destination_port_id": request.get("destination_port_id"),
        "destination_main_port_id": request.get("destination_main_port_id"),
        "container_size": request.get("container_size"),
        "container_type": request.get("container_type"),
        "commodity": request.get("commodity"),
        "rate_type": request.get("rate_type"),
    }
    conditions = [
        (getattr(FclFreightRateJob, key) == value) for key, value in params.items()
    ]
    conditions.append(FclFreightRateJob.status << ["pending", "backlog"])
    affected_ids = jsonable_encoder([
        job.id
        for job in FclFreightRateJob.select(FclFreightRateJob.id).where(*conditions)
    ])

    fcl_freight_rate_job = (
        FclFreightRateJob.update(update_params).where(*conditions).execute()
    )
    if fcl_freight_rate_job:
        for affected_id in affected_ids:
            set_jobs_mapping(affected_id, jsonable_encoder(request), str(id))
    return {"ids": affected_ids}


def set_jobs_mapping(jobs_id, data, id):
    audit_id = FclFreightRateJobMapping.create(
        source_id=id,
        job_id=jobs_id,
        performed_by_id=data.get("performed_by_id"),
        data=data,
    )
    return audit_id
