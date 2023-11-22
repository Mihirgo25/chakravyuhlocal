from services.air_freight_rate.models.air_freight_rate_local_jobs import AirFreightRateLocalJob
from services.air_freight_rate.models.air_freight_rate_local_job_mappings import (
    AirFreightRateLocalJobMapping,
)
from database.rails_db import get_user
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from services.air_freight_rate.models.air_services_audit import AirServiceAudit




def update_air_freight_rate_local_job_on_rate_addition(request, id):
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
        "trade_type": request.get("trade_type"),
    }
    conditions = [
        (getattr(AirFreightRateLocalJob, key) == value) for key, value in params.items()
    ]
    conditions.append(AirFreightRateLocalJob.status << ["pending", "backlog"])
    conditions.append(~(AirFreightRateLocalJob.sources.contains('live_booking')))
    affected_ids = jsonable_encoder([
        job.id for job in AirFreightRateLocalJob.select(AirFreightRateLocalJob.id).where(*conditions)
    ])
    air_freight_rate_local_job = AirFreightRateLocalJob.update(update_params).where(*conditions).execute()
    if air_freight_rate_local_job:
        update_mapping(affected_ids)
        for affected_id in affected_ids:
            create_audit(affected_id, jsonable_encoder(request))

    return {"ids": affected_ids}

def update_mapping(jobs_ids):
    update_params = {'status': "completed",  "updated_at": datetime.now()}
    AirFreightRateLocalJobMapping.update(update_params).where(AirFreightRateLocalJobMapping.job_id << jobs_ids).execute()

def create_audit(jobs_id, data):
    AirServiceAudit.create(
        action_name = 'delete',
        object_id = jobs_id,
        object_type = 'AirFreightRateLocalJob',
        performed_by_id=data.get("performed_by_id"),
        data=data
    )