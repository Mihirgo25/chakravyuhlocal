from database.db_session import db
from services.haulage_freight_rate.models.haulage_freight_rate_jobs import HaulageFreightRateJob
from services.haulage_freight_rate.models.haulage_freight_rate_job_mappings import HaulageFreightRateJobMapping
from database.rails_db import get_user
from datetime import datetime
from services.haulage_freight_rate.models.haulage_freight_rate_audit import HaulageFreightRateAudit

POSSIBLE_CLOSING_REMARKS = ['not_serviceable', 'rate_not_available', 'no_change_in_rate']


def delete_haulage_freight_rate_job(request):
    if request.get('closing_remarks') and request.get('closing_remarks') in POSSIBLE_CLOSING_REMARKS:
        update_params = {'status':'aborted', "closed_by_id": request.get('performed_by_id'), "closed_by": get_user(request.get('performed_by_id'))[0], "updated_at": datetime.now(), "closing_remarks": request.get('closing_remarks')}
    else:
        update_params = {'status':'completed', "closed_by_id": request.get('performed_by_id'), "closed_by": get_user(request.get('performed_by_id'))[0], "updated_at": datetime.now()}

    haulage_freight_rate_job = HaulageFreightRateJob.update(update_params).where(HaulageFreightRateJob.id == request['id'], HaulageFreightRateJob.status.not_in(['completed', 'aborted'])).execute()
    if haulage_freight_rate_job:
        create_audit(request['id'], request)

    return {'id' : request['id']}


def create_audit(jobs_id, data):
    HaulageFreightRateAudit.create(
        action_name = 'delete',
        object_id = jobs_id,
        object_type = 'HaulageFreightRateJob',
        data = data.get('data'),
        performed_by_id = data.get("performed_by_id")
    )