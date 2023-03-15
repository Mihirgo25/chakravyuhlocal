from services.fcl_freight_rate.models.fcl_freight_rate_free_day_request import FclFreightRateFreeDayRequest
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
from services.fcl_freight_rate.interaction.create_fcl_freight_rate import to_dict
from libs.logger import logger
from database.db_session import db

def delete_fcl_freight_rate_free_day_request(request):
    with db.atomic() as transaction:
        try:
            data = execute_transaction_code()
            return data
        except Exception as e:
            logger.error(e, exc_info = True)
            transaction.rollback()
            return 'Deletion Failed'


def execute_transaction_code(request):
    request = to_dict(request)
    object = find_object(request)

    if not object:
        raise Exception('fcl_freight_rate_free_day_request_id is invalid')

    object = object.first()
    object.status = 'inactive'
    object.closed_by_id = request['performed_by_id']
    if request['closing_remarks']:
      object.closing_remarks = request['closing_remarks']
   
    object.save()

    create_audit(request, object.id)
    object.delay_until(1.minute.from_now, queue: 'low', retry: 1).send_closed_notifications_to_sales_agent

    return {
      'fcl_freight_rate_free_day_request_id': request['fcl_freight_rate_free_day_request_id']
    }

def find_object(request):
    try:
        return FclFreightRateFreeDayRequest.where(id = request['fcl_freight_rate_free_day_request_id'], status = 'active') 
    except:
        return None


def create_audit(request, request_id):
    FclFreightRateAudit.create(
        action_name = 'delete',
        performed_by_id = request['performed_by_id'],
        data = {key:value for key,value in request.items() if key != 'fcl_freight_rate_free_day_request'},
        object_id = request_id,
        object_type = 'FclFreightRateFreeDayRequest'
    )