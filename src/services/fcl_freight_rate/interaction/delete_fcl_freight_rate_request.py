from services.fcl_freight_rate.models.fcl_freight_rate_request import FclFreightRateRequest
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
from fastapi import HTTPException
from services.fcl_freight_rate.models.fcl_freight_rate_task import FclFreightRateTask
from services.fcl_freight_rate.helpers.find_or_initiliaze import find_or_initialize
import time
def delete_fcl_freight_rate_request(request):
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
    print(time.time()-start)

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
