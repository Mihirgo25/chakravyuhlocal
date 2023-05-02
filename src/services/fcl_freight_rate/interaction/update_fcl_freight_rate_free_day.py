from services.fcl_freight_rate.models.fcl_freight_rate_free_day import FclFreightRateFreeDay
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
from fastapi import HTTPException
import datetime
from database.db_session import db

def update_fcl_freight_rate_free_day(request):
  object_type = 'Fcl_Freight_Rate_Free_Day' 
  query = "create table if not exists fcl_services_audits_{} partition of fcl_services_audits for values in ('{}')".format(object_type.lower(), object_type.replace("_","")) 
  db.execute_sql(query)
  with db.atomic():
    return execute_transaction_code(request)

def execute_transaction_code(request):
    from celery_worker import update_multiple_service_objects

    free_day = FclFreightRateFreeDay.get_by_id(request['id'])

    if request.get('free_limit'):
        free_day.free_limit = request.get('free_limit')
    if request.get('remarks'):
        free_day.remarks = request.get('remarks')
    if request.get('slabs'):
        free_day.slabs = request.get('slabs')

    free_day.update_special_attributes()
    free_day.rate_not_available_entry = False

    free_day.sourced_by_id = request.get("sourced_by_id")
    free_day.procured_by_id = request.get("procured_by_id")

    try:
        free_day.save()
    except:
        raise HTTPException(status_code=500, detail='fcl freight rate local did not save')

    update_multiple_service_objects.apply_async(kwargs={'object':free_day},queue='low')

    create_audit(request, free_day.id)

    return {
      'id': free_day.id
    }

def create_audit(request, free_day_id):

    audit_data = {'free_limit': request.get('free_limit'),'remarks': request.get('remarks'),'slabs': request.get('slabs')}

    try:
      FclServiceAudit.create(
        action_name = 'update',
        performed_by_id = request.get('performed_by_id'),
        bulk_operation_id = request.get('bulk_operation_id'),
        data = audit_data,
        object_id = free_day_id,
        object_type = 'FclFreightRateFreeDay'
      )
    except:
      raise HTTPException(status_code=500, detail='fcl freight audit for free day did not save')
