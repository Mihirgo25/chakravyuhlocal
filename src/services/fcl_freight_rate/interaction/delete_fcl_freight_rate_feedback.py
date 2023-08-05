from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from fastapi import HTTPException
from database.db_session import db
from celery_worker import update_multiple_service_objects,send_closed_notifications_to_sales_agent_feedback,send_closed_notifications_to_user_feedback
from playhouse.shortcuts import model_to_dict
from services.bramhastra.interactions.apply_feedback_fcl_freight_rate_statistic import apply_feedback_fcl_freight_rate_statistic
from services.bramhastra.request_params import ApplyFeedbackFclFreightRateStatistics
from fastapi.encoders import jsonable_encoder

def delete_fcl_freight_rate_feedback(request):
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
        
        set_stats(obj)

        if obj.source == 'spot_search' and obj.performed_by_type == 'user':
            send_closed_notifications_to_user_feedback.apply_async(kwargs={'object':obj},queue='critical')
        else:
            send_closed_notifications_to_sales_agent_feedback.apply_async(kwargs={'object':obj},queue='critical')

    return request['fcl_freight_rate_feedback_ids']


def find_objects(request):
    try:
        return FclFreightRateFeedback.select().where(FclFreightRateFeedback.id << request['fcl_freight_rate_feedback_ids'], FclFreightRateFeedback.status == 'active').execute()
    except:
        return None


def create_audit(request, freight_rate_feedback_id):
    FclFreightRateAudit.create(
    action_name = 'delete',
    performed_by_id = request['performed_by_id'],
    #### need to tackle what to send in data
    data = {'closing_remarks' : request['closing_remarks'], 'performed_by_id' : request['performed_by_id']},    #######already performed_by_id column is present do we need to also save it in data?
    object_id = freight_rate_feedback_id,
    object_type = 'FclFreightRateFeedback'
    
    
def set_stats(obj):
    action = 'delete'
    params = jsonable_encoder(model_to_dict(obj,only = [FclFreightRateFeedback.id,FclFreightRateFeedback.status,FclFreightRateFeedback.closed_by_id,FclFreightRateFeedback.closing_remarks]))
    apply_feedback_fcl_freight_rate_statistic(ApplyFeedbackFclFreightRateStatistics(action = action,params = params))
