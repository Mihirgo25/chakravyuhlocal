from services.fcl_freight_rate.models.fcl_freight_rate_local_jobs import FclFreightRateLocalJob
from services.fcl_freight_rate.models.fcl_freight_rate_local_job_mappings import (
    FclFreightRateLocalJobMapping,
)
from datetime import datetime
from database.rails_db import get_user
from fastapi.encoders import jsonable_encoder
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit




def update_fcl_freight_rate_local_job_on_rate_addition(request, id):
    update_params = {
        "status": "completed",
        "closed_by_id": request.get("performed_by_id"),
        "closed_by": get_user(request.get("performed_by_id"))[0],
        "updated_at": datetime.now()
    }

    params = {
        "port_id": request.get("port_id"),
        "main_port_id": request.get("main_port_id"),
        "container_size": request.get("container_size"),
        "container_type": request.get("container_type"),
        "commodity": request.get("commodity"),
        "rate_type": request.get("rate_type"),
        "trade_type": request.get("trade_type"),
    }
    conditions = [
        (getattr(FclFreightRateLocalJob, key) == value) for key, value in params.items()
    ]
    conditions.append(FclFreightRateLocalJob.status << ["pending", "backlog"])
    conditions.append(~(FclFreightRateLocalJob.sources.contains('live_booking')))
    affected_ids = jsonable_encoder([
        job.id
        for job in FclFreightRateLocalJob.select(FclFreightRateLocalJob.id).where(*conditions)
    ])

    fcl_freight_rate_local_job = (
        FclFreightRateLocalJob.update(update_params).where(*conditions).execute()
    )
    if fcl_freight_rate_local_job:
        update_mapping(affected_ids)
        for affected_id in affected_ids:
            create_audit(affected_id, jsonable_encoder(request))
    return {"ids": affected_ids}

def update_mapping(jobs_ids):
    update_params = {'status': "completed",  "updated_at": datetime.now()}
    FclFreightRateLocalJobMapping.update(update_params).where(FclFreightRateLocalJobMapping.job_id << jobs_ids).execute()

def create_audit(jobs_id, data):
    FclServiceAudit.create(
        action_name = 'delete',
        object_id = jobs_id,
        data = data,
        object_type = 'FclFreightRateLocalJob',
        performed_by_id=data.get("performed_by_id"),
    )
