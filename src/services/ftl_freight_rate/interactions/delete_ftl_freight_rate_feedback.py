from services.ftl_freight_rate.models.ftl_freight_rate_feedback import FtlFreightRateFeedback
from services.ftl_freight_rate.models.ftl_freight_rate_audit import FtlFreightRateAudit
from fastapi import HTTPException
from database.db_session import db
from services.ftl_freight_rate.interactions.delete_ftl_freight_rate_job import delete_ftl_freight_rate_job

def delete_ftl_freight_rate_feedback(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    objects = find_objects(request)

    if not objects:
      raise HTTPException(status_code=404, detail="Ftl Freight rate feedback id not found")

    for obj in objects:
        obj.status = 'inactive'
        obj.closed_by_id = request.get('performed_by_id')
        obj.closing_remarks = request.get('closing_remarks')

        try:
            obj.save()
        except:
            raise HTTPException(status_code=500, detail="Ftl Freight rate Feedback deletion failed")

        create_audit(request, obj.id)
        
        delete_ftl_freight_rate_job(request)

    return request['ftl_freight_rate_feedback_ids']


def find_objects(request):
    ftl_freight_rate_feedback = FtlFreightRateFeedback.select().where(FtlFreightRateFeedback.id << request['ftl_freight_rate_feedback_ids'], FtlFreightRateFeedback.status == 'active')
    if ftl_freight_rate_feedback.count() > 0:
        return ftl_freight_rate_feedback
    return None


def create_audit(request, freight_rate_feedback_id):
    data = {}
    for key,value in request.items():
        if key != freight_rate_feedback_id:
            data[key] = value

    FtlFreightRateAudit.create(
    action_name = 'delete',
    performed_by_id = request.get('performed_by_id'),
    data = data,
    object_id = freight_rate_feedback_id,
    object_type = 'FtlFreightRateFeedback'
    )
