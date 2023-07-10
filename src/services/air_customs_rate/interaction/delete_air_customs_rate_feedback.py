from services.air_customs_rate.models.air_customs_rate_feedback import AirCustomsRateFeedback
from services.air_customs_rate.models.air_customs_rate_audit import AirCustomsRateAudit
from database.db_session import db
from fastapi import HTTPException
from celery_worker import update_multiple_service_objects

def delete_air_customs_rate_feedback(request):
  with db.atomic():
    return execute_transaction_code(request)

def execute_transaction_code(request):
  air_feedback_objects = find_feedback_objects(request)
  if not air_feedback_objects:
    raise HTTPException(status_code=500, detail = 'Feedbacks Not Found')

  reverted_rate = {
     'rate_id':request.get('rate_id'),
     'customs_line_items':request.get('customs_line_items')
  }

  data = {key:value for key,value in request.items() if key != 'air_customs_rate_feedback_ids'},
  for object in air_feedback_objects:
    object.status = 'inactive'
    object.closed_by_id = request.get('performed_by_id')
    object.closing_remarks = request.get('closing_remarks')
    object.reverted_rate = reverted_rate

    try:
        object.save()
    except Exception as e:
        print("Exception in deleting feedback", e)

    create_audit_for_customs_feedback(request, object.id, data)
    update_multiple_service_objects.apply_async(kwargs={'object':object},queue='low')

  return {'air_customs_rate_feedback_ids' : request.get('air_customs_rate_feedback_ids')}

def find_feedback_objects(request):
  try:
    query_result = AirCustomsRateFeedback.select().where(
        AirCustomsRateFeedback.id << request.get('air_customs_rate_feedback_ids'),
        AirCustomsRateFeedback.status == 'active'
    ).execute()
  except:
    query_result = None
  return query_result

def create_audit_for_customs_feedback(request, object_id, data):
    AirCustomsRateAudit.create(
       action_name = 'delete',
       performed_by_id = request.get('performed_by_id'),
       object_id = object_id,
       object_type = 'AirCustomsRateFeedback',
       data = data
    )