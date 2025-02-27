from services.fcl_freight_rate.models.fcl_freight_rate_local_agent import FclFreightRateLocalAgent
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
from database.db_session import db
from fastapi import HTTPException

def create_fcl_freight_rate_local_agent(request):
  object_type = 'Fcl_Freight_Rate_Local_Agent' 
  query = "create table if not exists fcl_services_audits_{} partition of fcl_services_audits for values in ('{}')".format(object_type.lower(), object_type.replace("_","")) 
  db.execute_sql(query)
  with db.atomic():
    id = execute_transaction_code(request)
    return id



def execute_transaction_code(request):
    if type(request) != dict:
      request = request.__dict__
    
    create_params = get_create_params(request)

    local_agent_object = FclFreightRateLocalAgent.select().where(
      FclFreightRateLocalAgent.service_provider_id == request.get('service_provider_id'),
      FclFreightRateLocalAgent.location_id == request.get('location_id'),
      FclFreightRateLocalAgent.trade_type == request.get('trade_type'),
      FclFreightRateLocalAgent.status == request.get('status')
    ).first()

    if local_agent_object:
      return {
      'id': local_agent_object.id
    }
    else:
       local_agent_object = FclFreightRateLocalAgent(**create_params)
    
    local_agent_object.set_location_ids_and_type()
    try:
      if local_agent_object.validate():
          local_agent_object.save()
    except Exception as e:
      raise HTTPException(status_code = 500, detail = "Local Agent not saved")

    create_audit(request, local_agent_object.id)

    return {
      'id': local_agent_object.id
    }

def get_create_params(request):
    return {key:value for key,value in request.items() if key != 'performed_by_id'} 
  
def create_audit(request, local_agent_id):

    FclServiceAudit.create(
        action_name = 'create',
        performed_by_id = request['performed_by_id'],
        data = get_create_params(request),
        object_id = local_agent_id,
        object_type = 'FclFreightRateLocalAgent'
    )

