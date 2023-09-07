from services.air_freight_rate.models.air_freight_rate_jobs import AirFreightRateJobs
from services.air_freight_rate.models.air_freight_rate_jobs_mapping import (
    AirFreightRateJobsMapping,
)
from database.rails_db import get_user
from fastapi.encoders import jsonable_encoder



def update_air_freight_rate_job_on_rate_addition(request, id):
    update_params = {
        "status": "completed",
        "closed_by_id": request.get("performed_by_id"),
        "closed_by": get_user(request.get("performed_by_id"))[0],
    }
    params = {
        "origin_airport_id": request.get("origin_airport_id"),
        "destination_airport_id": request.get("destination_airport_id"),
        "commodity": request.get("commodity"),
        "rate_type": request.get("rate_type"),
        "commodity_type": request.get("commodity_type"),
        "commodity_sub_type": request.get("commodity_sub_type"),
        "stacking_type": request.get("stacking_type"),
        "operation_type": request.get("operation_type"),
    }
    conditions = [
        (getattr(AirFreightRateJobs, key) == value) for key, value in params.items()
    ]
    conditions.append(AirFreightRateJobs.status << ["pending", "backlog"])
    affected_ids = jsonable_encoder([
        job.id for job in AirFreightRateJobs.select(AirFreightRateJobs.id).where(*conditions)
    ])
    air_freight_rate_job = AirFreightRateJobs.update(update_params).where(*conditions).execute()
    if air_freight_rate_job:
        for affected_id in affected_ids:
            set_jobs_mapping(affected_id, jsonable_encoder(request), str(id))

    return {"ids": affected_ids}


def set_jobs_mapping(jobs_id, data, id):
    audit_id = AirFreightRateJobsMapping.create(
        source_id=id,
        job_id=jobs_id,
        performed_by_id=data.get("performed_by_id"),
        data=data,
    )
    return audit_id
