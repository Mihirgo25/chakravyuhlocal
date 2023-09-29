from services.haulage_freight_rate.models.haulage_freight_rate_request import HaulageFreightRateRequest
from services.haulage_freight_rate.models.haulage_freight_rate_audit import HaulageFreightRateAudit
from fastapi import HTTPException
from database.db_session import db
from services.haulage_freight_rate.haulage_celery_worker import delete_jobs_for_haulage_freight_rate_request_delay

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
        if request.get('reverted_rate_id') and request.get('reverted_rate'):
            obj.reverted_rate_id=request.get('reverted_rate_id')
            obj.reverted_rate = request.get('reverted_rate')
        
        obj.closed_by_id = request['performed_by_id']

        obj.closing_remarks = request.get('closing_remarks')

        try:
            obj.save()
        except:
            raise HTTPException(status_code=400, detail="Freight rate request deletion failed")

        create_audit(request, obj.id, obj.transport_mode)

    send_closed_notifications_to_sales_agent_function.apply_async(kwargs={'object':obj},queue='low')
    delete_jobs_for_haulage_freight_rate_request_delay.apply_async(kwargs = {'requirements': request}, queue='fcl_freight_rate')
    if request.get('haulage_freight_rate_request_ids'):
        return {'haulage_freight_rate_request_ids' : request['haulage_freight_rate_request_ids']}
    else:
        return {'trailer_freight_rate_request_ids' : request['trailer_freight_rate_request_ids']}



def find_objects(request):
    if request.get('haulage_freight_rate_request_ids'):
        object =  HaulageFreightRateRequest.select().where(HaulageFreightRateRequest.id << request['haulage_freight_rate_request_ids'] & (HaulageFreightRateRequest.status == 'active'))
    else:
        object =  HaulageFreightRateRequest.select().where(HaulageFreightRateRequest.id << request['trailer_freight_rate_request_ids'] & (HaulageFreightRateRequest.status == 'active'))

    if object.count() > 0:
        return object
    else:
        raise HTTPException(status_code=404, detail="Haulage Freight rate request id not found")


def create_audit(request, freight_rate_request_id, transport_mode):
    if 'trailer' in transport_mode:
        object_type="TrailerFreightRateRequest"
    else:
        object_type="HaulageFreightRateRequest"
    
    HaulageFreightRateAudit.create(
    action_name = 'delete',
    performed_by_id = request['performed_by_id'],
    data = {'closing_remarks' : request['closing_remarks'], 'performed_by_id' : request['performed_by_id']},
    object_id = freight_rate_request_id,
    object_type = object_type,
    sourced_by_id = request.get('sourced_by_id'),
    procured_by_id = request.get('procured_by_id')
    )
