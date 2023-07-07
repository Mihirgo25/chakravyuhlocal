from services.haulage_freight_rate.models.haulage_freight_rate_request import HaulageFreightRateRequest
from services.haulage_freight_rate.models.haulage_freight_rate_audit import HaulageFreightRateAudit
from fastapi import HTTPException
from database.db_session import db

def delete_haulage_freight_rate_request(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    """
    Delete Haulage Freight Rate Requests
    Response Format:
        {"ids": deleted_haulage_freight_rate_request_ids}
    """

    from celery_worker import send_closed_notifications_to_sales_agent_function
    objects = find_objects(request)

    for obj in objects:
        obj.status = 'inactive'
        obj.closed_by_id = request['performed_by_id']

        obj.closing_remarks = request.get('closing_remarks')

        try:
            obj.save()
        except:
            raise HTTPException(status_code=500, detail="Freight rate request deletion failed")

        create_audit(request, obj.id)

    send_closed_notifications_to_sales_agent_function.apply_async(kwargs={'object':obj},queue='low')
    return {'haulage_freight_rate_request_ids' : request['haulage_freight_rate_request_ids']}


def find_objects(request):
    object =  HaulageFreightRateRequest.select().where(HaulageFreightRateRequest.id << request['haulage_freight_rate_request_ids'] & (HaulageFreightRateRequest.status == 'active'))
    if object.count() > 0:
        return object
    else:
        raise HTTPException(status_code=400, detail="Haulage Freight rate request id not found")


def create_audit(request, freight_rate_request_id):
    HaulageFreightRateAudit.create(
    action_name = 'delete',
    performed_by_id = request['performed_by_id'],
    data = {'closing_remarks' : request['closing_remarks'], 'performed_by_id' : request['performed_by_id']},
    object_id = freight_rate_request_id,
    object_type = 'HaulageFreightRateRequest',
    sourced_by_id = request.get('sourced_by_id'),
    procured_by_id = request.get('procured_by_id')
    )
