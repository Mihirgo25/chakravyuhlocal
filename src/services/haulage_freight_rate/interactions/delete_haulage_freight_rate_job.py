from database.db_session import db
from services.haulage_freight_rate.models.haulage_freight_rate_jobs import HaulageFreightRateJob
from services.haulage_freight_rate.models.haulage_freight_rate_job_mappings import HaulageFreightRateJobMapping
from database.rails_db import get_user
from datetime import datetime
from services.haulage_freight_rate.models.haulage_freight_rate_audit import HaulageFreightRateAudit

POSSIBLE_CLOSING_REMARKS = ['not_serviceable', 'rate_not_available', 'no_change_in_rate']


def delete_haulage_freight_rate_job(request):
    
    if request.get("source_id"):
        job_ids = [ str(job.job_id) for job in HaulageFreightRateJobMapping.select(HaulageFreightRateJobMapping.job_id).where(HaulageFreightRateJobMapping.source_id == request['source_id'])]
        update_mapping('completed', job_ids) 
        request['data'] = {"reverted_flash_booking_ids": request.get('source_id')}
        create_audit(job_ids, request)
        return {"id": job_ids}
    
    if request.get('closing_remarks') and request.get('closing_remarks') in POSSIBLE_CLOSING_REMARKS:
        update_params = {'status':'aborted', "closed_by_id": request.get('performed_by_id'), "closed_by": get_user(request.get('performed_by_id'))[0], "updated_at": datetime.now(), "closing_remarks": request.get('closing_remarks')}
    else:
        update_params = {'status':'completed', "closed_by_id": request.get('performed_by_id'), "closed_by": get_user(request.get('performed_by_id'))[0], "updated_at": datetime.now()}
    
    job_ids = None
    if request.get('haulage_freight_rate_feedback_ids'):
        job_ids = [ str(job.job_id) for job in HaulageFreightRateJobMapping.select(HaulageFreightRateJobMapping.job_id).where(HaulageFreightRateJobMapping.source_id << request['haulage_freight_rate_feedback_ids'])]
    elif request.get('trailer_freight_rate_feedback_ids'):
        job_ids = [ str(job.job_id) for job in HaulageFreightRateJobMapping.select(HaulageFreightRateJobMapping.job_id).where(HaulageFreightRateJobMapping.source_id << request['trailer_freight_rate_feedback_ids'])]
    elif request.get('haulage_freight_rate_request_ids'):
        job_ids = [ str(job.job_id) for job in HaulageFreightRateJobMapping.select(HaulageFreightRateJobMapping.job_id).where(HaulageFreightRateJobMapping.source_id << request['haulage_freight_rate_request_ids'])]
    elif request.get('trailer_freight_rate_request_ids'):
        job_ids = [ str(job.job_id) for job in HaulageFreightRateJobMapping.select(HaulageFreightRateJobMapping.job_id).where(HaulageFreightRateJobMapping.source_id << request['trailer_freight_rate_request_ids'])]
    elif request.get("id"):
        job_ids = request.get("id")
    elif request.get("shipment_id"):
        job_ids = [ str(job.job_id) for job in HaulageFreightRateJobMapping.select(HaulageFreightRateJobMapping.job_id).where(HaulageFreightRateJobMapping.shipment_id == request['shipment_id'])]

 

    if not isinstance(job_ids, list):
        job_ids = [job_ids]

    haulage_freight_rate_job = HaulageFreightRateJob.update(update_params).where(HaulageFreightRateJob.id << job_ids, HaulageFreightRateJob.status.not_in(['completed', 'aborted'])).execute()

    if haulage_freight_rate_job:
        update_mapping(update_params['status'], job_ids)
        create_audit(job_ids, request)

    return {'id' : job_ids}


def update_mapping(status, jobs_ids):
    update_params = {'status': status,  "updated_at": datetime.now()}
    HaulageFreightRateJobMapping.update(update_params).where(HaulageFreightRateJobMapping.job_id << jobs_ids, HaulageFreightRateJobMapping.status.not_in(['completed', 'aborted'])).execute()

def create_audit(jobs_ids, data):
    for job_id in jobs_ids:
        HaulageFreightRateAudit.create(
            action_name = 'delete',
            object_id = job_id,
            object_type = 'HaulageFreightRateJob',
            data = data.get('data'),
            performed_by_id = data.get("performed_by_id")
        )