from services.air_customs_rate.models.air_customs_rate_request import AirCustomsRateRequest
from services.air_customs_rate.models.air_customs_rate_audit import AirCustomsRateAudit
from fastapi import HTTPException
from database.db_session import db
from celery_worker import update_multiple_service_objects

def delete_air_customs_rate_request(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
  request_objects = find_request_objects(request)
  if not request_objects:
    raise HTTPException(status_code=500, detail = 'Requests Not Found')

  data = {key:value for key,value in request.items() if key != 'air_customs_rate_request_ids'}
  for object in request_objects:
    object.status = 'inactive'
    object.closed_by_id = request.get('performed_by_id')
    object.closing_remarks = request.get('closing_remarks')

    try:
        object.save()
    except Exception as e:
        print("Exception in deleting request", e)

    update_multiple_service_objects.apply_async(kwargs={'object':object},queue='low')
    create_audit_for_customs_request(request, object, data)
    object.send_closed_notifications_to_sales_agent()

  return {'air_customs_rate_request_ids' : request.get('air_customs_rate_request_ids')}

def find_request_objects(request):
  try:
    query_result = AirCustomsRateRequest.select().where(
        AirCustomsRateRequest.id << request.get('air_customs_rate_request_ids'),
        AirCustomsRateRequest.status == 'active'
    ).execute()
  except:
    query_result = None
  return query_result

def create_audit_for_customs_request(request, object, data):
    AirCustomsRateAudit.create(
       action_name = 'delete',
       performed_by_id = request.get('performed_by_id'),
       object_id = object.id,
       object_type = 'AirCustomsRateRequest',
       data = data
    )