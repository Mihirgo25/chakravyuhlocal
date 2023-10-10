from database.db_session import db
from services.fcl_freight_rate.models.fcl_freight_rate_local_jobs import (
    FclFreightRateLocalJob,
)
from services.fcl_freight_rate.models.fcl_freight_rate_local_job_mappings import (
    FclFreightRateLocalJobMapping,
)
from database.rails_db import get_user
from datetime import datetime
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
from configs.global_constants import POSSIBLE_CLOSING_REMARKS_FOR_JOBS


def delete_fcl_freight_rate_local_job(request):
    
    if request.get("source_id"):
        job_ids = [ str(job.job_id) for job in FclFreightRateLocalJobMapping.select(FclFreightRateLocalJobMapping.job_id).where(FclFreightRateLocalJobMapping.source_id == request['source_id'])]
        update_mapping('completed', job_ids) 
        request['data'] = {"reverted_flash_booking_ids": request.get('source_id')}
        create_audit(job_ids, request)
        return {"id": job_ids}
    
    if (
        request.get("closing_remarks")
        and request.get("closing_remarks") in POSSIBLE_CLOSING_REMARKS_FOR_JOBS
    ):
        update_params = {
            "status": "aborted",
            "closed_by_id": request.get("performed_by_id"),
            "closed_by": get_user(request.get("performed_by_id"))[0],
            "updated_at": datetime.now(),
            "closing_remarks": request.get("closing_remarks"),
        }
    else:
        update_params = {
            "status": "completed",
            "closed_by_id": request.get("performed_by_id"),
            "closed_by": get_user(request.get("performed_by_id"))[0],
            "updated_at": datetime.now(),
        }
    job_ids = None    
    if request.get('fcl_freight_rate_local_feedback_ids'):
        job_ids = [ str(job.job_id) for job in FclFreightRateLocalJobMapping.select(FclFreightRateLocalJobMapping.job_id).where(FclFreightRateLocalJobMapping.source_id << request['fcl_freight_rate_local_feedback_ids'])]
    elif request.get('fcl_freight_rate_local_request_ids'):
        job_ids = [ str(job.job_id) for job in FclFreightRateLocalJobMapping.select(FclFreightRateLocalJobMapping.job_id).where(FclFreightRateLocalJobMapping.source_id << request['fcl_freight_rate_local_request_ids'])]
    elif request.get("id"):
        job_ids = request.get("id")
    elif request.get("shipment_id"):
        job_ids = [ str(job.job_id) for job in FclFreightRateLocalJobMapping.select(FclFreightRateLocalJobMapping.job_id).where(FclFreightRateLocalJobMapping.shipment_id == request['shipment_id'])]
    
    if not isinstance(job_ids, list):
        job_ids = [job_ids]
    
    fcl_freight_rate_local_job = FclFreightRateLocalJob.update(update_params).where(FclFreightRateLocalJob.id << job_ids, FclFreightRateLocalJob.status.not_in(['completed', 'aborted'])).execute()
    
    if fcl_freight_rate_local_job:
        update_mapping(update_params['status'], job_ids)
        create_audit(job_ids, request)

    return {"id": job_ids}


def update_mapping(status, jobs_ids):
    update_params = {'status': status,  "updated_at": datetime.now()}
    FclFreightRateLocalJobMapping.update(update_params).where(FclFreightRateLocalJobMapping.job_id << jobs_ids, FclFreightRateLocalJobMapping.status.not_in(['completed', 'aborted'])).execute()


def create_audit(jobs_ids, data):
    for job_id in jobs_ids:
        FclServiceAudit.create(
            action_name="delete",
            object_id=job_id,
            object_type="FclFreightRateLocalJob",
            data=data.get("data"),
            performed_by_id=data.get("performed_by_id"),
        )
