from services.air_freight_rate.models.air_freight_rate_jobs import AirFreightRateJob
from services.air_freight_rate.models.air_freight_rate_jobs_mapping import (
    AirFreightRateJobMapping,
)
from database.rails_db import get_user
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from services.air_freight_rate.models.air_services_audit import AirServiceAudit
from functools import reduce




def update_air_freight_rate_job_on_rate_addition(request, id):
    update_params = {
        "status": "completed",
        "closed_by_id": request.get("performed_by_id"),
        "closed_by": get_user(request.get("performed_by_id"))[0],
        "updated_at": datetime.now()
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
        (getattr(AirFreightRateJob, key) == value) for key, value in params.items()
    ]
    conditions.append(AirFreightRateJob.status << ["pending", "backlog"])
    exception_conditions = [(~AirFreightRateJob.sources.contains(tag)) for tag in ['live_booking','rate_request','rate_feedback']]
    combined_condition = reduce(lambda a, b: a & b, exception_conditions)
    conditions.append(combined_condition)
    affected_ids = jsonable_encoder([
        job.id for job in AirFreightRateJob.select(AirFreightRateJob.id).where(*conditions)
    ])
    air_freight_rate_job = AirFreightRateJob.update(update_params).where(*conditions).execute()
    if air_freight_rate_job:
        update_mapping(affected_ids)
        for affected_id in affected_ids:
            create_audit(affected_id, jsonable_encoder(request))

    return {"ids": affected_ids}

def update_mapping(jobs_ids):
    update_params = {'status': "completed",  "updated_at": datetime.now()}
    AirFreightRateJobMapping.update(update_params).where(AirFreightRateJobMapping.job_id << jobs_ids).execute()

def create_audit(jobs_id, data):
    AirServiceAudit.create(
        action_name = 'delete',
        object_id = jobs_id,
        object_type = 'AirFreightRateJob',
        performed_by_id=data.get("performed_by_id"),
        data=data
    )