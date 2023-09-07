from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJobs
from services.fcl_freight_rate.models.fcl_freight_rate_jobs_mapping import (
    FclFreightRateJobsMapping,
)
from database.rails_db import get_user


def update_fcl_freight_rate_job_on_rate_addition(request, id):
    update_params = {
        "status": "completed",
        "closed_by_id": request.get("performed_by_id"),
        "closed_by": get_user(request.get("performed_by_id"))[0],
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
        (getattr(FclFreightRateJobs, key) == value) for key, value in params.items()
    ]
    conditions.append(FclFreightRateJobs.status << ["pending", "backlog"])
    affected_ids = [
        job.id
        for job in FclFreightRateJobs.select(FclFreightRateJobs.id).where(*conditions)
    ]
    fcl_freight_rate_job = (
        FclFreightRateJobs.update(update_params).where(*conditions).execute()
    )
    if fcl_freight_rate_job:
        for affected_id in affected_ids:
            set_jobs_mapping(affected_id, request, id)

    return {"ids": affected_ids}


def set_jobs_mapping(jobs_id, data, id):
    audit_id = FclFreightRateJobsMapping.create(
        source_id=id,
        job_id=jobs_id,
        performed_by_id=data.get("performed_by_id"),
        data=data.get("data"),
    )
    return audit_id
