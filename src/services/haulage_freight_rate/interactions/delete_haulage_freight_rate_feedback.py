from services.haulage_freight_rate.models.haulage_freight_rate_feedback import HaulageFreightRateFeedback
from services.haulage_freight_rate.models.haulage_freight_rate_audit import HaulageFreightRateAudit
from fastapi import HTTPException
from database.db_session import db
from celery_worker import update_multiple_service_objects,send_closed_notifications_to_sales_agent_feedback

def delete_haulage_freight_rate_feedback(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    objects = find_objects(request)

    if not objects:
      raise HTTPException(status_code=400, detail="Freight rate feedback id not found")

    for obj in objects:
        obj.status = 'inactive'
        obj.closed_by_id = request['performed_by_id']

        obj.closing_remarks = request.get('closing_remarks')

        try:
            obj.save()
        except:
            raise HTTPException(status_code=500, detail="Freight rate local deletion failed")

        create_audit(request, obj.id)
        update_multiple_service_objects.apply_async(kwargs={'object':obj},queue='low')

        send_closed_notifications_to_sales_agent_feedback.apply_async(kwargs={'object':obj},queue='low')


    return {'ids': request['haulage_freight_rate_feedback_ids']}


def find_objects(request):
    try:
        return HaulageFreightRateFeedback.select().where(HaulageFreightRateFeedback.id << request['haulage_freight_rate_feedback_ids'], HaulageFreightRateFeedback.status == 'active').execute()
    except:
        return None


def create_audit(request, freight_rate_feedback_id):
    HaulageFreightRateAudit.create(
    action_name = 'delete',
    performed_by_id = request['performed_by_id'],
    data = {'closing_remarks' : request['closing_remarks'], 'performed_by_id' : request['performed_by_id']},
    object_id = freight_rate_feedback_id,
    object_type = 'HaulageFreightRateFeedback'
    )
