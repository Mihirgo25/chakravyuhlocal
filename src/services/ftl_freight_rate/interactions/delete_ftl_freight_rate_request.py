from services.ftl_freight_rate.models.ftl_freight_rate_request import FtlFreightRateRequest
from services.ftl_freight_rate.models.ftl_freight_rate_audit import FtlFreightRateAudit
from fastapi import HTTPException
from database.db_session import db

def delete_ftl_freight_rate_request(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    from celery_worker import send_closed_notifications_to_sales_agent_function
    objects = find_objects(request)

    if not objects:
        raise HTTPException(status_code=400, detail="Freight rate request id not found")

    for obj in objects:
        obj.status = 'inactve'
        obj.closed_by_id = request['performed_by_id']

        obj.closing_remarks = request.get('closing_remarks')

        try:
            obj.save()
        except:
            raise HTTPException(status_code=500, detail="Freight rate request deletion failed")

        create_audit(request, obj.id)

    send_closed_notifications_to_sales_agent_function.apply_async(kwargs={'object':obj},queue='low')
    return {'ftl_freight_rate_request_ids' : request['ftl_freight_rate_request_ids']}

def find_objects(request):
    try:
        return FtlFreightRateRequest.select().where(FtlFreightRateRequest.id << request['ftl_freight_rate_request_ids'] & (FtlFreightRateRequest.status == 'active')).execute()
    except:
        return None

def create_audit(request, freight_rate_request_id):
    data = {'closing_remarks' : request.get('closing_remarks'), 'performed_by_id' : request.get('performed_by_id')}

    FtlFreightRateAudit.create(
        action_name = 'delete',
        performed_by_id = request.get('performed_by_id'),
        data = data,
        object_id = freight_rate_request_id,
        object_type = 'FtlFreightRateRequest'
    )
