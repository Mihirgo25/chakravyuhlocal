from database.db_session import db
from services.fcl_customs_rate.models.fcl_customs_rate_jobs import FclCustomsRateJob
from services.fcl_customs_rate.models.fcl_customs_rate_job_mappings import FclCustomsRateJobMapping
from database.rails_db import get_user
from datetime import datetime
from services.fcl_customs_rate.models.fcl_customs_rate_audit import FclCustomsRateAudit

POSSIBLE_CLOSING_REMARKS = ['not_serviceable', 'rate_not_available', 'no_change_in_rate']


def delete_fcl_customs_rate_job(request):
    if request.get('closing_remarks') and request.get('closing_remarks') in POSSIBLE_CLOSING_REMARKS:
        update_params = {'status':'aborted', "closed_by_id": request.get('performed_by_id'), "closed_by": get_user(request.get('performed_by_id'))[0], "updated_at": datetime.now(), "closing_remarks": request.get('closing_remarks')}
    else:
        update_params = {'status':'completed', "closed_by_id": request.get('performed_by_id'), "closed_by": get_user(request.get('performed_by_id'))[0], "updated_at": datetime.now()}

    fcl_customs_rate_job = FclCustomsRateJob.update(update_params).where(FclCustomsRateJob.id == request['id'], FclCustomsRateJob.status.not_in(['completed', 'aborted'])).execute()
    if fcl_customs_rate_job:
        create_audit(request['id'], request)

    return {'id' : request['id']}


def create_audit(jobs_id, data):
    FclCustomsRateAudit.create(
        action_name = 'delete',
        object_id = jobs_id,
        object_type = 'FclCustomsRateJob',
        data = data.get('data'),
        performed_by_id = data.get("performed_by_id")
    )