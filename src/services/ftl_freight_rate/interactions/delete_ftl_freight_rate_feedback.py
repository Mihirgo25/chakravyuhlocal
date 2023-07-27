from services.ftl_freight_rate.models.ftl_freight_rate_feedback import FtlFreightRateFeedback
from services.ftl_freight_rate.models.ftl_freight_rate_audit import FtlFreightRateAudit
from fastapi import HTTPException
from database.db_session import db

def delete_ftl_freight_rate_feedback(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    objects = find_objects(request)

    if not objects:
      raise HTTPException(status_code=400, detail="Ftl Freight rate feedback id not found")

    for obj in objects:
        obj.status = 'inactive'
        obj.closed_by_id = request.get('performed_by_id')
        obj.closing_remarks = request.get('closing_remarks')

        try:
            obj.save()
        except:
            raise HTTPException(status_code=500, detail="Ftl Freight rate Feedback deletion failed")

        create_audit(request, obj.id)

    return request['ftl_freight_rate_feedback_ids']


def find_objects(request):
    try:
        return FtlFreightRateFeedback.select().where(FtlFreightRateFeedback.id << request['ftl_freight_rate_feedback_ids'], FtlFreightRateFeedback.status == 'active').execute()
    except:
        return None


def create_audit(request, freight_rate_feedback_id):
    FtlFreightRateAudit.create(
    action_name = 'delete',
    performed_by_id = request.get('performed_by_id'),
    data = {key:value for key,value in request.items() if key != freight_rate_feedback_id},    
    object_id = freight_rate_feedback_id,
    object_type = 'FtlFreightRateFeedback'
    )
