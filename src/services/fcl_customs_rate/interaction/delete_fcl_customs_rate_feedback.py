from services.fcl_customs_rate.models.fcl_customs_rate_feedback import FclCustomsRateFeedback
from services.fcl_customs_rate.models.fcl_customs_rate_audit import FclCustomsRateAudit
from database.db_session import db
from fastapi import HTTPException
from libs.get_multiple_service_objects import get_multiple_service_objects
from services.fcl_customs_rate.interaction.delete_fcl_customs_rate_job import (
    delete_fcl_customs_rate_job
)
from celery_worker import (
   update_spot_search_delay
)

def delete_fcl_customs_rate_feedback(request):
  with db.atomic():
    return execute_transaction_code(request)

def execute_transaction_code(request):
  feedback_objects = find_feedback_objects(request)
  if not feedback_objects:
    raise HTTPException(status_code=500, detail = 'Feedbacks Not Found')

  data = {key:value for key,value in request.items() if key != 'fcl_customs_rate_feedback_ids'},
  for object in feedback_objects:
    object.status = 'inactive'
    object.closed_by_id = request.get('performed_by_id')
    object.closing_remarks = request.get('closing_remarks')
    object.reverted_rate = request.get('reverted_rate')

    try:
        object.save()
    except Exception as e:
        print("Exception in deleting feedback", e)
    if "rate_added" in request.get("closing_remarks",[]):
      update_spot_search_delay.apply_async(
        kwargs = {"data":{
          "only_rates_update_required" : True,
          "id" : object.source_id
        }},
        queue = "critical"
      )

    create_audit_for_customs_feedback(request, object, data)
    get_multiple_service_objects(object)
    delete_fcl_customs_rate_job(request)
  return {'fcl_customs_rate_feedback_ids' : request.get('fcl_customs_rate_feedback_ids')}


def find_feedback_objects(request):
  try:
    query_result = FclCustomsRateFeedback.select().where(
        FclCustomsRateFeedback.id << request.get('fcl_customs_rate_feedback_ids'),
        FclCustomsRateFeedback.status == 'active'
    ).execute()
  except:
    query_result = None
  return query_result


def create_audit_for_customs_feedback(request, object, data):
    FclCustomsRateAudit.create(
       action_name = 'delete',
       performed_by_id = request.get('performed_by_id'),
       object_id = object.id,
       object_type = 'FclCustomsRateFeedback',
       data = data
    )