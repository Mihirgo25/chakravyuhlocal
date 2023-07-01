from services.fcl_customs_rate.models.fcl_customs_rate_request import FclCustomsRateRequest
from services.fcl_customs_rate.models.fcl_customs_rate_audit import FclCustomsRateAudit
from fastapi import HTTPException
from database.db_session import db
from celery_worker import update_multiple_service_objects

def delete_fcl_customs_rate_request_data(request):
    with db.atomic():
        return delete_fcl_customs_rate_request(request)

def delete_fcl_customs_rate_request(request):
  request_objects = find_request_objects(request)
  if not request_objects:
    raise HTTPException(status_code=500, detail = 'Requests Not Found')
    
  data = {key:value for key,value in request.items() if key != 'fcl_customs_rate_request_ids'},
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
  return {'fcl_customs_rate_request_ids' : request.get('fcl_customs_rate_request_ids')}

def find_request_objects(request):
  try:
    query_result = FclCustomsRateRequest.select().where(
        FclCustomsRateRequest.id << request.get('fcl_customs_rate_request_ids'),
        FclCustomsRateRequest.status == 'active'
    ).execute()
  except:
    query_result = None
  return query_result

def create_audit_for_customs_request(request, object, data):
    FclCustomsRateAudit.create(
       action_name = 'delete',
       performed_by_id = request.get('performed_by_id'),
       object_id = object.id,
       object_type = 'FclCustomsRateRequest',
       data = data
    )