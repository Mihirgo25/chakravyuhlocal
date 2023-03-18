from services.fcl_freight_rate.models.fcl_freight_rate_local_agent import FclFreightRateLocalAgent
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from database.db_session import db
from fastapi import HTTPException
# from libs.logger import logger
from datetime import datetime
import time
def update_fcl_freight_rate_local_agent(request):
  with db.atomic() as transaction:
    try:
      data = execute_transaction_code(request)
      return data
    except Exception as e:
      # logger.error(e, exc_info = True)
      transaction.rollback()
      return 'Updation Failed'

def execute_transaction_code(request):
  # local_agent_object = get_local_agent_object(**{'id':request['id']})
  
  update_params = get_update_params(request)
  update_params['updated_at'] = datetime.now()
  local_agent_object = FclFreightRateLocalAgent.get_or_none(FclFreightRateLocalAgent.id == request['id'])

  if local_agent_object:

    for key,value in update_params.items():
      setattr(local_agent_object,key,value)
    
    if local_agent_object.validate_status() and local_agent_object.validate_service_provider():
      local_agent_object.save()
      

  else:
    raise HTTPException(status_code = '', detail = '{} is invalid'.format(request['id']))

 
  # try:
  #   local_agent_object.execute()
  # except:
  #   raise HTTPException(status_code = '', detail = '{} is invalid'.format(request['id']))

  # create_audits(request, request['id'])

  return {
    'id': request['id'] 
  }

def get_update_params(request):
  params = {key:value for key,value in request.items() if key not in ['id','performed_by_id']}
  return params

def create_audits(request, local_agent_object_id):  
  FclFreightRateAudit.create(
    action_name = 'update',
    performed_by_id = request['performed_by_id'],
    data = get_update_params(request),
    object_type = 'FclFreightRateLocalAgent',
    object_id = local_agent_object_id
  )