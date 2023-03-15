from services.fcl_freight_rate.models.fcl_freight_rate_local_agent import FclFreightRateLocalAgent
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
from database.db_session import db
from datetime import datetime
from services.fcl_freight_rate.helpers.find_or_initiliaze import find_or_initialize
# from libs.logger import logger
from fastapi import HTTPException
import time
def create_fcl_freight_rate_local_agent(request):
  with db.atomic() as transaction:
      try:
        id = execute_transaction_code(request)
        return id
      except Exception as e:
          # logger.error(e, exc_info=True)
          transaction.rollback()
          return "Creation Failed"


def execute_transaction_code(request):
    if type(request) != dict:
      request = request.__dict__
    
    # create_params = get_create_params(request)
    
    local_agent_object,found = find_or_initialize(FclFreightRateLocalAgent,**create_params)


    if found:
      return {
      'id': local_agent_object.id
      }
    
    local_agent_object.set_location_ids_and_type()
    try:
      if local_agent_object.validate():
          
          local_agent_object.save()
    except Exception as e:
      print(e)
      raise HTTPException(status_code = 500, detail = "Local Agent not saved")

    create_audit(request, local_agent_object.id)
    
    
    return {
      'id': local_agent_object.id
    }

def get_create_params(request):
    return {key:value for key,value in request.items() if key != 'performed_by_id'}
    
# def find_or_initialize(**kwargs):
#   try:
#     obj = FclFreightRateLocalAgent.get(**kwargs)
#     obj.updated_at = datetime.now()
#     return obj,True
#   except FclFreightRateLocalAgent.DoesNotExist:
#     obj = FclFreightRateLocalAgent(**kwargs)
#     return obj,False

def create_audit(request, local_agent_id):

    FclFreightRateAudit.create(
        action_name = 'create',
        performed_by_id = request['performed_by_id'],
        data = get_create_params(request),
        object_id = local_agent_id,
        object_type = 'FclFreightRateLocalAgent'
    )

