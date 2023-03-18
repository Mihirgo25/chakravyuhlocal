from services.fcl_freight_rate.models.fcl_freight_rate_free_day_request import FclFreightRateFreeDayRequest
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from fastapi import HTTPException
from database.db_session import db

def delete_fcl_freight_rate_free_day_request(request):
    with db.atomic() as transaction:
        try:
            return execute_transaction_code(request)
        except Exception as e:
            transaction.rollback()
            return e

def execute_transaction_code(request):
    object = find_objects(request)

    if not object:
      raise HTTPException(status_code=499, detail="Freight rate free day request id not found")

    object.status = 'inactive'
    object.closed_by_id = request['performed_by_id']

    # if request.get('closing_remarks'):
    object.closing_remarks = request.get('closing_remarks')

    try:
        object.save()
    except Exception as e:
        # self.errors.append(('fcl_freight_rate_feedback_ids', str(e)))
        # self.errors.merge!(obj.errors)
        raise HTTPException(status_code=499, detail="Freight rate free day request deletion failed")

    create_audit(request, object.id)
    # obj.delay(queue: 'low').send_closed_notifications_to_sales_agent

    return {'fcl_freight_rate_free_day_request_id' : request['fcl_freight_rate_free_day_request_id']}


def find_objects(request):
    try:
        return FclFreightRateFreeDayRequest.select().where(FclFreightRateFreeDayRequest.id << request['fcl_freight_rate_free_day_request_id'] & (FclFreightRateFreeDayRequest.status == 'active'))
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
