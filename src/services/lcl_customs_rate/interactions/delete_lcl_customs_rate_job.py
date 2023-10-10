from database.db_session import db
from services.lcl_customs_rate.models.lcl_customs_rate_jobs import LclCustomsRateJob
from services.lcl_customs_rate.models.lcl_customs_rate_job_mappings import (
    LclCustomsRateJobMapping,
)
from database.rails_db import get_user
from datetime import datetime
from services.lcl_customs_rate.models.lcl_customs_rate_audit import LclCustomsRateAudit

POSSIBLE_CLOSING_REMARKS = [
    "not_serviceable",
    "rate_not_available",
    "no_change_in_rate",
]


def delete_lcl_customs_rate_job(request):
    
    if request.get("source_id"):
        job_ids = [ str(job.job_id) for job in LclCustomsRateJobMapping.select(LclCustomsRateJobMapping.job_id).where(LclCustomsRateJobMapping.source_id == request['source_id'])]
        update_mapping('completed', job_ids) 
        request['data'] = {"reverted_flash_booking_ids": request.get('source_id')}
        create_audit(job_ids, request)
        return {"id": job_ids}

    if isinstance(request.get("closing_remarks"), list):
        request["closing_remarks"] = request.get("closing_remarks")[0]
    
    if (
        request.get("closing_remarks")
        and request.get("closing_remarks") in POSSIBLE_CLOSING_REMARKS
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
    if request.get('lcl_customs_rate_feedback_ids'):
        job_ids = [ str(job.job_id) for job in LclCustomsRateJobMapping.select(LclCustomsRateJobMapping.job_id).where(LclCustomsRateJobMapping.source_id << request['lcl_customs_rate_feedback_ids'])]
    elif request.get('lcl_customs_rate_request_ids'):
        job_ids = [ str(job.job_id) for job in LclCustomsRateJobMapping.select(LclCustomsRateJobMapping.job_id).where(LclCustomsRateJobMapping.source_id << request['lcl_customs_rate_request_ids'])]
    elif request.get("id"):
        job_ids = request.get("id")
    elif request.get("shipment_id"):
        job_ids = [ str(job.job_id) for job in LclCustomsRateJobMapping.select(LclCustomsRateJobMapping.job_id).where(LclCustomsRateJobMapping.shipment_id == request['shipment_id'])]
    
    if not isinstance(job_ids, list):
        job_ids = [job_ids]
    
    lcl_customs_rate_job = LclCustomsRateJob.update(update_params).where(LclCustomsRateJob.id << job_ids, LclCustomsRateJob.status.not_in(['completed', 'aborted'])).execute()
    
    if lcl_customs_rate_job:
        update_mapping(update_params['status'], job_ids)
        create_audit(job_ids, request)

    return {"id": job_ids}


def update_mapping(status, job_ids):
    update_params = {'status':status, "updated_at": datetime.now()}
    LclCustomsRateJobMapping.update(update_params).where(LclCustomsRateJobMapping.job_id << job_ids, LclCustomsRateJobMapping.status.not_in(['completed', 'aborted'])).execute()


def create_audit(jobs_ids, data):
    for job_id in jobs_ids:
        LclCustomsRateAudit.create(
            action_name="delete",
            object_id=job_id,
            object_type="LclCustomsRateJob",
            data=data.get("data"),
            performed_by_id=data.get("performed_by_id"),
        )
