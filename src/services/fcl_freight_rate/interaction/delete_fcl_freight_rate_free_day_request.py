from services.fcl_freight_rate.models.fcl_freight_rate_free_day_request import FclFreightRateFreeDayRequest
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from fastapi import HTTPException
from database.db_session import db
from celery_worker import send_closed_notifications_to_sales_agent_free_day_request

def delete_fcl_freight_rate_free_day_request(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    object = find_objects(request)

    if not object:
      raise HTTPException(status_code=404, detail="Freight rate free day request id not found")

    object.status = 'inactive'
    object.closed_by_id = request['performed_by_id']

    object.closing_remarks = request.get('closing_remarks')

    try:
        object.save()
    except:
        raise HTTPException(status_code=500, detail="Freight rate free day request deletion failed")

    create_audit(request, object.id)
    send_closed_notifications_to_sales_agent_free_day_request.apply_async(kwargs={'object':object},queue='low')

    return {'fcl_freight_rate_free_day_request_id' : request['fcl_freight_rate_free_day_request_id']}


def find_objects(request):
    try:
        return FclFreightRateFreeDayRequest.select().where(FclFreightRateFreeDayRequest.id << request['fcl_freight_rate_free_day_request_id'], FclFreightRateFreeDayRequest.status == 'active').execute()
    except:
        return None


def create_audit(request, freight_rate_free_day_request_id):
    FclFreightRateAudit.create(
    action_name = 'delete',
    performed_by_id = request['performed_by_id'],
    data = {'closing_remarks' : request['closing_remarks'], 'performed_by_id' : request['performed_by_id']},    #######already performed_by_id column is present do we need to also save it in data?
    object_id = freight_rate_free_day_request_id,
    object_type = 'FclFreightRateFreeDayRequest'
    )
