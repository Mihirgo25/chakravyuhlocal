from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJob
from services.fcl_freight_rate.models.fcl_freight_rate_job_mappings import (
    FclFreightRateJobMapping,
)
from datetime import datetime
from database.rails_db import get_user
from fastapi.encoders import jsonable_encoder
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit




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
    conditions.append(~(FclFreightRateJob.sources.contains('live_booking')))
    conditions.append(~(FclFreightRateJob.sources.contains('rate_request')))
    conditions.append(~(FclFreightRateJob.sources.contains('rate_feedback')))
    affected_ids = jsonable_encoder([
        job.id
        for job in FclFreightRateJob.select(FclFreightRateJob.id).where(*conditions)
    ])

    fcl_freight_rate_job = (
        FclFreightRateJob.update(update_params).where(*conditions).execute()
    )
    if fcl_freight_rate_job:
        update_mapping(affected_ids)
        for affected_id in affected_ids:
            create_audit(affected_id, jsonable_encoder(request))
    return {"ids": affected_ids}

def update_mapping(jobs_ids):
    update_params = {'status': "completed",  "updated_at": datetime.now()}
    FclFreightRateJobMapping.update(update_params).where(FclFreightRateJobMapping.job_id << jobs_ids).execute()

def create_audit(jobs_id, data):
    FclServiceAudit.create(
        action_name = 'delete',
        object_id = jobs_id,
        data = data,
        object_type = 'FclFreightRateJob',
        performed_by_id=data.get("performed_by_id"),
    )
