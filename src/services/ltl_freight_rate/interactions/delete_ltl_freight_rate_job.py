from database.db_session import db
from services.ltl_freight_rate.models.ltl_freight_rate_jobs import LtlFreightRateJob
from services.ltl_freight_rate.models.ltl_freight_rate_job_mappings import LtlFreightRateJobMapping
from database.rails_db import get_user
from datetime import datetime
from services.ltl_freight_rate.models.ltl_freight_rate_audit import LtlFreightRateAudit
from configs.global_constants import POSSIBLE_CLOSING_REMARKS_FOR_JOBS


def delete_ltl_freight_rate_job(request):
    
    if request.get("source_id"):
        job_ids = [ str(job.job_id) for job in LtlFreightRateJobMapping.select(LtlFreightRateJobMapping.job_id).where(LtlFreightRateJobMapping.source_id == request['source_id'])]
        update_mapping('completed', job_ids) 
        request['data'] = {"reverted_flash_booking_ids": request.get('source_id')}
        create_audit(job_ids, request)
        return {"id": job_ids}

    if isinstance(request.get("closing_remarks"), list):
        request["closing_remarks"] = request.get("closing_remarks")[0]
    
    if request.get('closing_remarks') and request.get('closing_remarks') in POSSIBLE_CLOSING_REMARKS_FOR_JOBS:
        update_params = {
            'status':'aborted',
            "closed_by_id": request.get('performed_by_id'),
            "closed_by": get_user(request.get('performed_by_id'))[0] if request.get("performed_by_id") else None,
            "updated_at": datetime.now(),
            "closing_remarks": request.get('closing_remarks')
            }
    else:
        update_params = {
            'status':'completed',
            "closed_by_id": request.get('performed_by_id'),
            "closed_by": get_user(request.get('performed_by_id'))[0] if request.get("performed_by_id") else None,
            "updated_at": datetime.now()
            }

    job_ids = None
    if request.get('ltl_freight_rate_feedback_ids'):
        job_ids = [ str(job.job_id) for job in LtlFreightRateJobMapping.select(LtlFreightRateJobMapping.job_id).where(LtlFreightRateJobMapping.source_id << request['ltl_freight_rate_feedback_ids'])]
    elif request.get('ltl_freight_rate_request_ids'):
        job_ids = [ str(job.job_id) for job in LtlFreightRateJobMapping.select(LtlFreightRateJobMapping.job_id).where(LtlFreightRateJobMapping.source_id << request['ltl_freight_rate_request_ids'])]
    elif request.get("id"):
        job_ids = request.get("id")
    elif request.get("shipment_id"):
        job_ids = [ str(job.job_id) for job in LtlFreightRateJobMapping.select(LtlFreightRateJobMapping.job_id).where(LtlFreightRateJobMapping.shipment_id == request['shipment_id'])]
    
    if not isinstance(job_ids, list):
        job_ids = [job_ids]
    
    ltl_freight_rate_job = LtlFreightRateJob.update(update_params).where(LtlFreightRateJob.id << job_ids, LtlFreightRateJob.status.not_in(['completed', 'aborted'])).execute()
    
    if ltl_freight_rate_job:
        update_mapping(update_params['status'], job_ids)
        create_audit(job_ids, request)

    return {"id": job_ids}


def update_mapping(status, jobs_ids):
    update_params = {'status': status,  "updated_at": datetime.now()}
    LtlFreightRateJobMapping.update(update_params).where(LtlFreightRateJobMapping.job_id << jobs_ids, LtlFreightRateJobMapping.status.not_in(['completed', 'aborted'])).execute()


def create_audit(jobs_ids, data):
    for job_id in jobs_ids:
        LtlFreightRateAudit.create(
            action_name = 'delete',
            object_id = job_id,
            object_type = 'LtlFreightRateJob',
            data = data.get('data'),
            performed_by_id = data.get("performed_by_id")
        )