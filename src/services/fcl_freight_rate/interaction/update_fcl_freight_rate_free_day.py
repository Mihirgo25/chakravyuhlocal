from services.fcl_freight_rate.models.fcl_freight_rate_free_day import FclFreightRateFreeDay
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
from fastapi import HTTPException
import datetime


def update_fcl_freight_rate_free_day(request):
    #### write a ciondition where if atleast one of free_limit,remarks or slabs is present then only execute update otherwise it's of no use
    free_day = FclFreightRateFreeDay.get_by_id(request['id'])

    if request.get('free_limit'):
        free_day.free_limit = request.get('free_limit')
    if request.get('remarks'):
        free_day.remarks = request.get('remarks')
    if request.get('slabs'):
        free_day.slabs = request.get('slabs')

    free_day.update_special_attributes()
    free_day.updated_at = datetime.datetime.now()

    try:
        free_day.save()
    except:
        raise HTTPException(status_code=499, detail='fcl freight rate local did not save')
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
      raise HTTPException(status_code=499, detail='fcl freight audit did not save')
    # print('audit', audit.__dict__)

def get_audit_params(request):
    

    return {
      
    }
