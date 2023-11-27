from fastapi import HTTPException
from database.db_session import db 
from services.air_freight_rate.models.air_freight_rate_local_feedback import AirFreightRateLocalFeedback
from celery_worker import send_closed_notifications_to_sales_agent_feedback
from services.air_freight_rate.models.air_services_audit import AirServiceAudit
from libs.get_multiple_service_objects import get_multiple_service_objects
from services.air_freight_rate.interactions.delete_air_freight_rate_local_job import delete_air_freight_rate_local_job
from celery_worker import (
    update_spot_search_delay
)

def delete_air_freight_rate_local_feedback(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    objects = find_feedback_objects(request)
    if not objects :
        raise HTTPException(status_code=400, detail='Invalid Rate Feedback')
    
    for obj in objects:
        obj.status='inactive'
        obj.reverted_rate = request.get('reverted_rate')
        obj.closed_by_id=request.get('performed_by_id')
        obj.closing_remarks = request.get('closing_remarks')
        
        try:
            obj.save()
        except:
            raise HTTPException(status_code=500, detail='deletion failed')

        if "rate_added" in request.get('closing_remarks',[]):
            update_spot_search_delay.apply_async(
                kwargs = {"data":{
                    "only_rates_update_required" : True,
                    "id" : obj.source_id
                }},
                queue = "critical"
            )

        create_audit(request,obj.id)
        get_multiple_service_objects(obj)

        send_closed_notifications_to_sales_agent_feedback.apply_async(kwargs={'object':obj},queue='critical')

        delete_air_freight_rate_local_job(request)

    return {"air_freight_rate_local_feedback_ids":request['air_freight_rate_local_feedback_ids']}

def create_audit(request,id):
    AirServiceAudit.create(
        action_name='delete',
        performed_by_id=request.get('performed_by_id'),
        data={key:value for key,value in request.items() if key not in ['air_freight_rate_local_feedback_ids'] },
        object_id=id,
        object_type='AirFreightRateLocalFeedback'
    )

def find_feedback_objects(request):
    objects = AirFreightRateLocalFeedback.select().where(
        AirFreightRateLocalFeedback.id<<request['air_freight_rate_local_feedback_ids'],
        AirFreightRateLocalFeedback.status=='active'
    ).execute()
    return objects