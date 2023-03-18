from services.fcl_freight_rate.models.fcl_freight_rate_free_day import FclFreightRateFreeDay
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from fastapi import HTTPException
import datetime
from database.db_session import db


def update_fcl_freight_rate_free_day(request):
  with db.atomic() as transaction:
        try:
          return execute_transaction_code(request)
        except Exception as e:
            transaction.rollback()
            return e

def execute_transaction_code(request):

    free_day = FclFreightRateFreeDay.get_by_id(request['id'])

    if request.get('free_limit'):
        free_day.free_limit = request.get('free_limit')
    if request.get('remarks'):
        free_day.remarks = request.get('remarks')
    if request.get('slabs'):
        free_day.slabs = request.get('slabs')

    free_day.updated_at = datetime.datetime.now()
    free_day.update_special_attributes()

    try:
        free_day.save()
    except:
        raise HTTPException(status_code=403, detail='fcl freight rate local did not save')

    create_audit(request, free_day.id)

    return {
      'id': free_day.id
    }

def create_audit(request, free_day_id):

    audit_data = {'free_limit': request.get('free_limit'),'remarks': request.get('remarks'),'slabs': request.get('slabs')}

    try:
      FclFreightRateAudit.create(
        action_name = 'update',
        performed_by_id = request.get('performed_by_id'),
        bulk_operation_id = request.get('bulk_operation_id'),
        procured_by_id = request.get('procured_by_id'),
        sourced_by_id = request.get('sourced_by_id'),
        data = audit_data,
        object_id = free_day_id,
        object_type = 'FclFreightRateFreeDay'
      )
    except:
      raise HTTPException(status_code=403, detail='fcl freight audit for free day did not save')
