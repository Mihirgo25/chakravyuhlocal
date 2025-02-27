from datetime import datetime
from fastapi import HTTPException
from database.db_session import db 
from services.air_freight_rate.models.air_freight_rate_feedback import AirFreightRateFeedback
from celery_worker import send_closed_notifications_to_sales_agent_feedback,send_closed_notifications_to_user_feedback
from services.air_freight_rate.models.air_services_audit import AirServiceAudit
from libs.get_multiple_service_objects import get_multiple_service_objects
from database.rails_db import (
    get_organization_partner,
)
from celery_worker import (
    update_spot_search_delay
)
from services.air_freight_rate.interactions.delete_air_freight_rate_job import delete_air_freight_rate_job

def delete_air_freight_rate_feedback(request):
    with db.atomic():
        return execute_transaction_code(request)
    
def execute_transaction_code(request):
    objects=find_object(request)
    if not objects :
        raise HTTPException(status_code=404, detail='Invalid Rate Feedback')
    
    for obj in objects:
        obj.status='inactive'

        if request.get('reverted_rate_id') and request.get('reverted_rate'):
            obj.reverted_rate_id=request.get('reverted_rate_id')
            obj.reverted_rate = request.get('reverted_rate')
        obj.closed_by_id=request.get('performed_by_id')
        
        if request.get('closing_remarks'):
            obj.closing_remarks=request.get('closing_remarks')
        
        try:
            obj.save()
        except:
            raise HTTPException(status_code=500, detail='deletion failed')

        if "rate_added" in request.get('closing_remarks',[]):
            update_spot_search_delay.apply_async(
                kwargs = {"data":{
                    "only_rates_update_required" : True,
                    "id" : obj.source_id,
                    "is_disliked_cache_key": "spot_search_rate_is_disliked_{}_{}_{}".format(str(obj.source_id),str(obj.air_freight_rate_id),str(obj.validity_id))
                }},
                queue = "critical"
            )

        create_audit(request,obj.id)
        get_multiple_service_objects(obj)

        id = str(obj.performed_by_org_id)
        org_users = get_organization_partner(id)
         
        if  obj.performed_by_type == 'user' and org_users  and obj.source != 'checkout':
            send_closed_notifications_to_user_feedback.apply_async(kwargs={'object':obj},queue="critical") 
        else:
            send_closed_notifications_to_sales_agent_feedback.apply_async(kwargs={'object':obj},queue='critical')    

        delete_air_freight_rate_job(request)  
    return {"air_freight_rate_feedback_ids":request['air_freight_rate_feedback_ids']}      

def create_audit(request,id):
    AirServiceAudit.create(
        action_name='delete',
        performed_by_id=request.get('performed_by_id'),
        data={key:value for key,value in request.items() if key not in ['air_freight_rate_feedback_ids'] },
        object_id=id,
        object_type='AirFreightRateFeedback'
    )    

def find_object(request):
    try:
        objects=AirFreightRateFeedback.select().where(AirFreightRateFeedback.id<<request['air_freight_rate_feedback_ids'],AirFreightRateFeedback.status=='active').execute()
    except:
        objects=None
    return objects