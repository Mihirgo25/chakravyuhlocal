from services.fcl_freight_rate.models.fcl_freight_rate_request import FclFreightRateRequest
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from fastapi import HTTPException
from services.fcl_freight_rate.models.fcl_freight_rate_task import FclFreightRateTask
import time
from database.db_session import db

def delete_fcl_freight_rate_request(request):
    with db.atomic() as transaction:
        try:
            return execute_transaction_code(request)
        except Exception as e:
            transaction.rollback()
            return e

def execute_transaction_code(request):
    start = time.time()
    objects = find_objects(request)

    if not objects:
      raise HTTPException(status_code=404, detail="Freight rate request id not found")

    for obj in objects:
        obj.status = 'inactive'
        obj.closed_by_id = request['performed_by_id']

        obj.closing_remarks = request.get('closing_remarks')

        try:
            obj.save()
        except Exception as e:

            raise HTTPException(status_code=499, detail="Freight rate request deletion failed")

        create_audit(request, obj.id)
        # obj.delay(queue: 'low').send_closed_notifications_to_sales_agent

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
    object_type = 'FclFreightRateRequest'
    )
