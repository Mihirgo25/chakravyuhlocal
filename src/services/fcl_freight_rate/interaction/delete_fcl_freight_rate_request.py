from services.fcl_freight_rate.models.fcl_freight_rate_request import FclFreightRateRequest
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from fastapi import HTTPException
from database.db_session import db
from fastapi.encoders import jsonable_encoder
from services.bramhastra.request_params import ApplyFclFreightRateRequestStatistic
from playhouse.shortcuts import model_to_dict
from services.bramhastra.interactions.apply_fcl_freight_rate_request_statistic import apply_fcl_freight_rate_request_statistic

def delete_fcl_freight_rate_request(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    from celery_worker import send_closed_notifications_to_sales_agent_function
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

    send_closed_notifications_to_sales_agent_function.apply_async(kwargs={'object':obj},queue='low')
    
    set_stats(obj)
    
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
    
    
def set_stats(obj):
    action = 'delete'
    params = jsonable_encoder(model_to_dict(obj,only = [FclFreightRateRequest.id,FclFreightRateRequest.status,FclFreightRateRequest.closed_by_id,FclFreightRateRequest.closing_remarks]))
    apply_fcl_freight_rate_request_statistic(ApplyFclFreightRateRequestStatistic(action = action,params = params))
