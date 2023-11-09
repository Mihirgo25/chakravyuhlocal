from database.db_session import db
from services.ftl_freight_rate.models.ftl_freight_rate_jobs import FtlFreightRateJob
from services.ftl_freight_rate.models.ftl_freight_rate_job_mappings import FtlFreightRateJobMapping
from database.rails_db import get_user
from datetime import datetime
from services.ftl_freight_rate.models.ftl_services_audit import FtlServiceAudit
from configs.global_constants import POSSIBLE_CLOSING_REMARKS_FOR_JOBS


def delete_ftl_freight_rate_job(request):
    
    if request.get("source_id"):
        job_ids = [ str(job.job_id) for job in FtlFreightRateJobMapping.select(FtlFreightRateJobMapping.job_id).where(FtlFreightRateJobMapping.source_id == request['source_id'])]
        update_reverted_mapping('reverted', job_ids) 
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
    if request.get('ftl_freight_rate_feedback_ids'):
        job_ids = [ str(job.job_id) for job in FtlFreightRateJobMapping.select(FtlFreightRateJobMapping.job_id).where(FtlFreightRateJobMapping.source_id << request['ftl_freight_rate_feedback_ids'])]
    elif request.get('ftl_freight_rate_request_ids'):
        job_ids = [ str(job.job_id) for job in FtlFreightRateJobMapping.select(FtlFreightRateJobMapping.job_id).where(FtlFreightRateJobMapping.source_id << request['ftl_freight_rate_request_ids'])]
    elif request.get("id"):
        job_ids = request.get("id")
    elif request.get("shipment_id") and request.get('service_id'):
        job_ids = [ str(job.job_id) for job in FtlFreightRateJobMapping.select(FtlFreightRateJobMapping.job_id).where((FtlFreightRateJobMapping.shipment_id == request['shipment_id']) & (FtlFreightRateJobMapping.shipment_service_id == request['service_id']))]
    
    if not isinstance(job_ids, list):
        job_ids = [job_ids]
    
    ftl_freight_rate_job = FtlFreightRateJob.update(update_params).where(FtlFreightRateJob.id << job_ids, FtlFreightRateJob.status.not_in(['completed', 'aborted'])).execute()
    
    if ftl_freight_rate_job:
        update_mapping(update_params['status'], job_ids)
        # create_audit(job_ids, request)

    return {"id": job_ids}

def update_reverted_mapping(status, jobs_ids):
    update_params = {'status': status,  "updated_at": datetime.now()}
    FtlFreightRateJobMapping.update(update_params).where(FtlFreightRateJobMapping.job_id << jobs_ids, FtlFreightRateJobMapping.status.not_in(['completed', 'aborted'])).execute()

def update_mapping(status, jobs_ids):
    update_params = {'status': status,  "updated_at": datetime.now()}
    FtlFreightRateJobMapping.update(update_params).where(FtlFreightRateJobMapping.job_id << jobs_ids, FtlFreightRateJobMapping.status.not_in(['completed', 'aborted', 'reverted'])).execute()


def create_audit(jobs_ids, data):
    for job_id in jobs_ids:
        FtlServiceAudit.create(
            action_name = 'delete',
            object_id = job_id,
            object_type = 'FtlFreightRateJob',
            data = data.get('data'),
            performed_by_id = data.get("performed_by_id")
        )