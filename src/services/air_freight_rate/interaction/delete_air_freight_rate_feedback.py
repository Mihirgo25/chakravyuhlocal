from datetime import datetime
from fastapi import HTTPException
from database.db_session import db 
from services.air_freight_rate.models.air_freight_rate_feedback import AirFreightRateFeedbacks
from celery_worker import update_multiple_service_objects,send_closed_notifications_to_sales_agent_feedback
from services.air_freight_rate.models.air_freight_rate_audit import AirFreightRateAudits
def delete_air_freight_rate_feedback(request):
    with db.atomic():
        return execute_transaction_code(request)
    
def execute_transaction_code(request):
    objects=find_object(request)
    if not objects :
        raise HTTPException(status_code=400, detail='id not found')
    
    for obj in objects:
        obj.status='inactive'

        if request.get('reverted_rate_id') and request.get('reverted_validity_id'):
            obj.reverted_rate_id=request.get('reverted_rate_id')
            obj.reverted_validity_id=request.get('reverted_validity_id')
        obj.closed_by_id=request.get('performed_by_id')
        
        if request.get('closing_remarks'):
            obj.closing_remarks=request.get('closing_remarks')
        
        try:
            obj.save()
        except:
            raise HTTPException(status_code=500, detail='deletion failed')
    

        create_audit(request,obj.id)
        update_multiple_service_objects.apply_async(kwargs={'object':obj},queue='low')

        send_closed_notifications_to_sales_agent_feedback.apply_async(kwargs={'object':obj},queue='low')  

    return {"id":request['air_freight_rate_feedback_ids']}      

def create_audit(request,id):
    AirFreightRateAudits.create(
        action_name='delete',
        performed_by_id=request.get('performed_by_id'),
        data={key:value for key,value in request.items() if key not in ['air_freight_rate_feedback_ids'] },
        object_id=id,
        object_type='AirFreightRateFeedback'
    )    

def find_object(request):
    try:
        objects=AirFreightRateFeedbacks.select().where(AirFreightRateFeedbacks.id<<request['air_freight_rate_feedback_ids'],AirFreightRateFeedbacks.status=='active').execute()
    except:
        objects=None
    return objects