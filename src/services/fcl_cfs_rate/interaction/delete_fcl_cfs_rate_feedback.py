from services.fcl_cfs_rate.models.fcl_cfs_rate_feedback import FclCfsRateFeedback
from services.fcl_cfs_rate.models.fcl_cfs_rate_audit import FclCfsRateAudit
from fastapi import HTTPException
from database.db_session import db
from libs.get_multiple_service_objects import get_multiple_service_objects
from services.fcl_cfs_rate.interaction.delete_fcl_cfs_rate_job import delete_fcl_cfs_rate_job

def delete_fcl_cfs_rate_feedback(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    from services.fcl_cfs_rate.fcl_cfs_celery_worker import send_notifications_to_sales_agent_fcl_cfs_feedback_delay
    objects = find_feedback_objects(request)

    if not objects:
      raise HTTPException(status_code=400, detail="Cfs rate feedback is not found")
    
    for obj in objects:
        obj.status = 'inactive'
        obj.closed_by_id = request.get('performed_by_id')
        obj.closing_remarks = request.get('closing_remarks')
        obj.reverted_rate = request.get('reverted_rate')

        try:
            obj.save()
        except:
            raise HTTPException(status_code=500, detail="Cfs rate feedback deletion failed")
        create_audit(request, obj.id)
        get_multiple_service_objects(obj)
        send_notifications_to_sales_agent_fcl_cfs_feedback_delay.apply_async(kwargs={'object':obj},queue='low')

        delete_fcl_cfs_rate_job(request)

    return {'fcl_cfs_rate_feedback_ids' : request['fcl_cfs_rate_feedback_ids']}

def find_feedback_objects(request):
    query = FclCfsRateFeedback.select().where(
        FclCfsRateFeedback.id << request['fcl_cfs_rate_feedback_ids'],
        FclCfsRateFeedback.status == 'active').execute()
    return query
    
def create_audit(request, cfs_rate_feedback_id):
    data = {'closing_remarks' : request.get('closing_remarks'), 'performed_by_id' : request.get('performed_by_id')}

    FclCfsRateAudit.create(
        action_name = 'delete',
        performed_by_id = request.get('performed_by_id'),
        data = data,
        object_id = cfs_rate_feedback_id,
        object_type = 'FclCfsRateFeedback'
    )