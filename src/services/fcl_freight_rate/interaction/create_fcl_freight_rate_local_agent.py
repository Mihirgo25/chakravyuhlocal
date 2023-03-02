from services.fcl_freight_rate.models.fcl_freight_rate_local_agent import FclFreightRateLocalAgent
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
from database.db_session import db
from datetime import datetime
from libs.logger import logger

def create_fcl_freight_rate_local_agent(request):
    with db.atomic() as transaction:
        try:
            id = execute_transaction_code(request)
            return id
        except:
            transaction.rollback()
            return "Creation Failed"


def execute_transaction_code(request):
    create_params = get_create_params(request)
    local_agent_object = find_or_initialize(**create_params)
    
    
    if validations(local_agent_object) and local_agent_object.set_location_ids_and_type():
        local_agent_object.save()
    else:
        return None

    create_audit(request, local_agent_object.id)
    
    return {
      'id': local_agent_object.id
    }

def get_create_params(request):
    return {key:value for key,value in request.items() if key != 'performed_by_id'} | { 'status': request['status'] }
    
def find_or_initialize(**kwargs):
  try:
    obj = FclFreightRateLocalAgent.get(**kwargs)
    obj.updated_at = datetime.now()
  except FclFreightRateLocalAgent.DoesNotExist:
    obj = FclFreightRateLocalAgent(**kwargs)
  return obj

def create_audit(request, local_agent_id):
    FclFreightRateAudit.create(
        action_name = 'create',
        performed_by_id = request['performed_by_id'],
        data = get_create_params(request),
        object_id = local_agent_id,
        object_type = 'FclFreightRateLocalAgent'
    )

def validations(local_agent_object):
    if local_agent_object.validate_service_provider() and local_agent_object.validate_trade_type() and local_agent_object.validate_status() and local_agent_object.valid_uniqueness():
        return True
    return False