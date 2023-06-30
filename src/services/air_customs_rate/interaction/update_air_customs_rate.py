from services.air_customs_rate.models.air_customs_rate import AirCustomsRate
from services.air_customs_rate.models.air_customs_rate_audit import AirCustomsRateAudit
from fastapi import HTTPException
from database.db_session import db


def update_air_customs_rate(request):
    with db.atomic():
        return execute_transaction_code(request)
    
def execute_transaction_code(request):
    rate_object = find_rate_object(request)
    if not rate_object:
        raise HTTPException(status_code=500, detail='Rate Not Found')
    
    rate_object.line_items = request.get('line_items')
    rate_object.procured_by_id = request.get('procured_by_id')
    rate_object.sourced_by_id = request.get('sourced_by_id')

    try:
        rate_object.save()
    except Exception as e:
        print("Exception in updating rate", e)

    rate_object.update_line_item_messages()
    create_audit_for_updating_rate(request, rate_object)

    return {'id': rate_object.id}

def find_rate_object(request):
    try:
        rate_object = AirCustomsRate.get_by_id(request['id'])
    except:
        rate_object = None
    return rate_object

def create_audit_for_updating_rate(request, rate_object):
    data = {key:value for key, value in request.items() if key not in ['performed_by_id', 'id', 'bulk_operation_id','procured_by_id','sourced_by_id']}
    
    AirCustomsRateAudit.create(
      action_name =  'update',
      performed_by_id =  request.get('performed_by_id'),
      bulk_operation_id =  request.get('bulk_operation_id'),
      object_id = rate_object.id,
      object_type = 'AirCustomsRate',
      data = data
    )