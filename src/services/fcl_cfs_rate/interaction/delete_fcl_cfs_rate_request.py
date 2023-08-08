from services.fcl_cfs_rate.models.fcl_cfs_rate_request import FclCfsRateRequest
from services.fcl_cfs_rate.models.fcl_cfs_rate_audit import FclCfsRateAudit
from fastapi import HTTPException
from database.db_session import db
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects

def delete_fcl_cfs_rate_request(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    from celery_worker import send_closed_notifications_to_sales_agent_function
    objects = find_objects(request)

    if not objects:
      raise HTTPException(status_code=400, detail="Cfs rate request is not found")
    
    for obj in objects:
        obj.status = 'inactive'
        obj.closed_by_id = request.get('performed_by_id')

        if request.get('closing_remarks'):
                obj.closing_remarks = request.get('closing_remarks')

        try:
            obj.save()
        except:
            raise HTTPException(status_code=500, detail="Cfs rate request deletion failed")
        create_audit(request, obj.id)
        get_multiple_service_objects(obj)

    send_closed_notifications_to_sales_agent_function.apply_async(kwargs={'object':obj},queue='low')

    return {'fcl_cfs_rate_request_ids' : request['fcl_cfs_rate_request_ids']}

def find_objects(request):
    try:
        return FclCfsRateRequest.select().where(FclCfsRateRequest.id << request['fcl_cfs_rate_request_ids'] & (FclCfsRateRequest.status == 'active')).execute()
    except:
        return None
    
def create_audit(request, cfs_rate_request_id):
    data = {'closing_remarks' : request.get('closing_remarks'), 'performed_by_id' : request.get('performed_by_id')}

    FclCfsRateAudit.create(
        action_name = 'delete',
        performed_by_id = request.get('performed_by_id'),
        data = data,
        object_id = cfs_rate_request_id,
        object_type = 'FclCfsRateRequest'
    )