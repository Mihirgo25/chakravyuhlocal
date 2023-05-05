from services.fcl_freight_rate.models.fcl_freight_rate_weight_limit import FclFreightRateWeightLimit
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
from fastapi import HTTPException
from datetime import datetime
from database.db_session import db

def update_fcl_freight_rate_weight_limit(request):
  object_type = 'Fcl_Freight_Rate_Weight_Limit' 
  query = "create table if not exists fcl_services_audits_{} partition of fcl_services_audits for values in ('{}')".format(object_type.lower(), object_type.replace("_","")) 
  db.execute_sql(query)
  with db.atomic():
    return execute_transaction_code(request)

def execute_transaction_code(request):
    from celery_worker import update_multiple_service_objects

    weight_limit = FclFreightRateWeightLimit.get_by_id(request['id'])
    if request.get('free_limit'):
        weight_limit.free_limit = request.get('free_limit')
    if request.get('remarks'):
        weight_limit.remarks = request.get('remarks')
    if request.get('slabs'):
        weight_limit.slabs = request.get('slabs')

    weight_limit.updated_at = datetime.now()
   
    weight_limit.update_special_attributes()

    weight_limit.sourced_by_id = request.get("sourced_by_id")
    weight_limit.procured_by_id = request.get("procured_by_id")

    try:
        weight_limit.save()
    except:
        raise HTTPException(status_code=500, detail='fcl freight rate local did not save')

    update_multiple_service_objects.apply_async(kwargs={'object':weight_limit},queue='critical')

    create_audit(request, weight_limit.id)

    return {
      'id': weight_limit.id
    }

def create_audit(request, weight_limit_id):

    audit_data = {'free_limit': request.get('free_limit'),'remarks': request.get('remarks'),'slabs': request.get('slabs')}

    try:
      FclServiceAudit.create(
        action_name = 'update',
        performed_by_id = request.get('performed_by_id'),
        data = audit_data,
        object_id = weight_limit_id,
        object_type = 'FclFreightRateWeightLimit'
      )
    except:
      raise HTTPException(status_code=500, detail='fcl freight audit for weight limit did not save')
