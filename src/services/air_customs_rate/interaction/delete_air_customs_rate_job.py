from database.db_session import db
from services.air_customs_rate.models.air_customs_rate_jobs import AirCustomsRateJob
from services.air_customs_rate.models.air_customs_rate_job_mappings import AirCustomsRateJobMapping
from database.rails_db import get_user
from datetime import datetime
from services.air_customs_rate.models.air_customs_rate_audit import AirCustomsRateAudit
from configs.global_constants import POSSIBLE_CLOSING_REMARKS_FOR_JOBS


def delete_air_customs_rate_job(request):
    
    if request.get("source_id"):
        job_ids = [ str(job.job_id) for job in AirCustomsRateJobMapping.select(AirCustomsRateJobMapping.job_id).where(AirCustomsRateJobMapping.source_id == request['source_id'])]
        update_mapping('completed', job_ids) 
        request['data'] = {"reverted_flash_booking_ids": request.get('source_id')}
        create_audit(job_ids, request)
        return {"id": job_ids}
    
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
    if request.get('air_customs_rate_feedback_ids'):
        job_ids = [ str(job.job_id) for job in AirCustomsRateJobMapping.select(AirCustomsRateJobMapping.job_id).where(AirCustomsRateJobMapping.source_id << request['air_customs_rate_feedback_ids'])]
    elif request.get('air_customs_rate_request_ids'):
        job_ids = [ str(job.job_id) for job in AirCustomsRateJobMapping.select(AirCustomsRateJobMapping.job_id).where(AirCustomsRateJobMapping.source_id << request['air_customs_rate_request_ids'])]
    elif request.get("id"):
        job_ids = request.get("id")
    elif request.get("shipment_id"):
        job_ids = [ str(job.job_id) for job in AirCustomsRateJobMapping.select(AirCustomsRateJobMapping.job_id).where(AirCustomsRateJobMapping.shipment_id == request['shipment_id'])]
    
    if not isinstance(job_ids, list):
        job_ids = [job_ids]
    
    air_freight_rate_job = AirCustomsRateJob.update(update_params).where(AirCustomsRateJob.id << job_ids, AirCustomsRateJob.status.not_in(['completed', 'aborted'])).execute()
    
    if air_freight_rate_job:
        update_mapping(update_params['status'], job_ids)
        create_audit(job_ids, request)

    return {"id": job_ids}


def create_audit(jobs_ids, data):
    for job_id in jobs_ids:
        AirCustomsRateAudit.create(
            action_name = 'delete',
            object_id = job_id,
            object_type = 'AirCustomsRateJob',
            performed_by_id = data.get("performed_by_id"),
            data = data.get('data')
        )
        
def update_mapping(status, job_ids):
    update_params = {'status':status, "updated_at": datetime.now()}
    AirCustomsRateJobMapping.update(update_params).where(AirCustomsRateJobMapping.job_id << job_ids, AirCustomsRateJobMapping.status.not_in(['completed', 'aborted'])).execute()
    