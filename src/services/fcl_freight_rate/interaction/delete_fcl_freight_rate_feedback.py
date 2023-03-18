from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from fastapi import HTTPException
from database.db_session import db

def delete_fcl_freight_rate_feedback(request):
    with db.atomic() as transaction:
        try:
            return execute_transaction_code(request)
        except Exception as e:
            transaction.rollback()
            return e

def execute_transaction_code(request):
    objects = find_objects(request)

    if not objects:
      raise HTTPException(status_code=499, detail="Freight rate feedback id not found")

    for obj in objects:
        obj.status = 'inactive'
        obj.closed_by_id = request['performed_by_id']

        # if request.get('closing_remarks'):
        obj.closing_remarks = request.get('closing_remarks')

        try:
            obj.save()
        except Exception as e:
            # self.errors.append(('fcl_freight_rate_feedback_ids', str(e)))
            # self.errors.merge!(obj.errors)
            raise HTTPException(status_code=499, detail="Freight rate local deletion failed")

        create_audit(request, obj.id)
        # obj.delay(queue: 'low').send_closed_notifications_to_sales_agent

    return request['fcl_freight_rate_feedback_ids']


def find_objects(request):
    try:
        return FclFreightRateFeedback.select().where(FclFreightRateFeedback.id << request['fcl_freight_rate_feedback_ids'] & (FclFreightRateFeedback.status == 'active'))
    except:
        return None


def create_audit(request, freight_rate_feedback_id):
    FclFreightRateAudit.create(
    action_name = 'delete',
    performed_by_id = request['performed_by_id'],
    #### need to tackle what to send in data
    data = {'closing_remarks' : request['closing_remarks'], 'performed_by_id' : request['performed_by_id']},    #######already performed_by_id column is present do we need to also save it in data?
    object_id = freight_rate_feedback_id,
    object_type = 'FclFreightRateFeedback'
    )
