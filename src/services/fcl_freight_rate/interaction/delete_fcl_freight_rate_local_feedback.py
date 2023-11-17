from services.fcl_freight_rate.models.fcl_freight_rate_local_feedback import FclFreightRateLocalFeedback
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from fastapi import HTTPException
from database.db_session import db
from database.rails_db import (
    get_organization_partner,
)
from celery_worker import update_multiple_service_objects,send_closed_notifications_to_sales_agent_feedback,send_closed_notifications_to_user_feedback
from services.bramhastra.celery import send_feedback_delete_stats_in_delay
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_local_job import delete_fcl_freight_rate_local_job

def delete_fcl_freight_rate_local_feedback(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    objects = find_feedback_objects(request)

    if not objects:
      raise HTTPException(status_code=400, detail="Freight rate Feedback not found")

    for obj in objects:
        obj.status = 'inactive'
        obj.closed_by_id = request['performed_by_id']
        obj.closing_remarks = request.get('closing_remarks')
        obj.reverted_rate = request.get('reverted_rate')

        try:
            obj.save()
        except:
            raise HTTPException(status_code=500, detail="Freight rate local feedback deletion failed")

        create_audit(request, obj.id)
        update_multiple_service_objects.apply_async(kwargs={'object':obj},queue='low')

        id = str(obj.performed_by_org_id)
        org_users = get_organization_partner(id)

        if obj.performed_by_type == 'user' and org_users and  obj.source != 'checkout':
            send_closed_notifications_to_user_feedback.apply_async(kwargs={'object':obj},queue='critical')
        else:
            send_closed_notifications_to_sales_agent_feedback.apply_async(kwargs={'object':obj},queue='critical')

        delete_fcl_freight_rate_local_job(request)

    return request['fcl_freight_rate_local_feedback_ids']

def find_feedback_objects(request):
    objects = FclFreightRateLocalFeedback.select().where(
        FclFreightRateLocalFeedback.id << request['fcl_freight_rate_local_feedback_ids'], 
        FclFreightRateLocalFeedback.status == 'active').execute()
    return objects

def create_audit(request, freight_rate_feedback_id):
    FclFreightRateAudit.create(
        action_name = 'delete',
        performed_by_id = request['performed_by_id'],
        data = {'closing_remarks' : request['closing_remarks'], 'performed_by_id' : request['performed_by_id']},
        object_id = freight_rate_feedback_id,
        object_type = 'FclFreightRateLocalFeedback'
    )