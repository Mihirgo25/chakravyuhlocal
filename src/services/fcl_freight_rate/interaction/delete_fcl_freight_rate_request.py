from services.fcl_freight_rate.models.fcl_freight_rate_request import FclFreightRateRequest
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from fastapi import HTTPException
from database.db_session import db
from database.rails_db import (
    get_organization_partner,
)

def delete_fcl_freight_rate_request(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    from celery_worker import send_closed_notifications_to_sales_agent_function,send_closed_notifications_to_user_request
    objects = find_objects(request)

    if not objects:
      raise HTTPException(status_code=400, detail="Freight rate request id not found")

    for obj in objects:
        obj.status = 'inactive'
        obj.closed_by_id = request['performed_by_id']

        obj.closing_remarks = request.get('closing_remarks')

        try:
            obj.save()
        except:
            raise HTTPException(status_code=500, detail="Freight rate request deletion failed")

        create_audit(request, obj.id)

        id = str(obj.performed_by_org_id)
        org_users = get_organization_partner(id)

        if obj.performed_by_type == 'user' and org_users and  obj.source != 'checkout':
            send_closed_notifications_to_user_request.apply_async(kwargs={'object':obj},queue='critical')
        else:
            send_closed_notifications_to_sales_agent_function.apply_async(kwargs={'object':obj},queue='critical')
    
        # from services.bramhastra.celery import send_delete_request_stats_in_delay
        # send_delete_request_stats_in_delay.apply_async(kwargs = {'obj':obj},queue = 'statistics')

    return {'fcl_freight_rate_request_ids' : request['fcl_freight_rate_request_ids']}


def find_objects(request):
    try:
        return FclFreightRateRequest.select().where(FclFreightRateRequest.id << request['fcl_freight_rate_request_ids'] & (FclFreightRateRequest.status == 'active')).execute()
    except:
        return None


def create_audit(request, freight_rate_request_id):
    FclFreightRateAudit.create(
    action_name = 'delete',
    performed_by_id = request['performed_by_id'],
    data = {'closing_remarks' : request['closing_remarks'], 'performed_by_id' : request['performed_by_id']},    #######already performed_by_id column is present do we need to also save it in data?
    object_id = freight_rate_request_id,
    object_type = 'FclFreightRateRequest')
