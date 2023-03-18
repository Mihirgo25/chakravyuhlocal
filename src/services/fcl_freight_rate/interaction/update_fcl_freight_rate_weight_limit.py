from services.fcl_freight_rate.models.fcl_freight_rate_weight_limit import FclFreightRateWeightLimit
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from fastapi import HTTPException
from datetime import datetime
from database.db_session import db

def update_fcl_freight_rate_weight_limit(request):
  with db.atomic() as transaction:
        try:
          return execute_transaction_code(request)
        except Exception as e:
            transaction.rollback()
            return e

def execute_transaction_code(request):
    weight_limit = FclFreightRateWeightLimit.get_by_id(request['id'])

    if request.get('free_limit'):
        weight_limit.free_limit = request.get('free_limit')
    if request.get('remarks'):
        weight_limit.remarks = request.get('remarks')
    if request.get('slabs'):
        weight_limit.slabs = request.get('slabs')

    weight_limit.updated_at = datetime.now()
   
    weight_limit.update_special_attributes()
    try:
        weight_limit.save()
    except:
        raise HTTPException(status_code=403, detail='fcl freight rate local did not save')

    create_audit(request, weight_limit.id)

    return {
      'id': weight_limit.id
    }

def create_audit(request, weight_limit_id):

    audit_data = {'free_limit': request.get('free_limit'),'remarks': request.get('remarks'),'slabs': request.get('slabs')}

    try:
      FclFreightRateAudit.create(
        action_name = 'update',
        performed_by_id = request.get('performed_by_id'),
        procured_by_id = request.get('procured_by_id'),
        sourced_by_id = request.get('sourced_by_id'),
        data = audit_data,
        object_id = weight_limit_id,
        object_type = 'FclFreightRateWeightLimit'
      )
    except:
      raise HTTPException(status_code=499, detail='fcl freight audit for weight limit did not save')
