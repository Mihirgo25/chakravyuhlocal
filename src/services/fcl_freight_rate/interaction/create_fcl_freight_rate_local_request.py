from services.fcl_freight_rate.models.fcl_freight_rate_local_request import FclFreightRateLocalRequest
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
from services.fcl_freight_rate.helpers.find_or_initialize import find_or_initialize
from datetime import datetime
import uuid
from database.db_session import db

def create_fcl_freight_rate_local_request(request):
    # with db.atomic() as transaction:
    #     try:
    return execute_transaction_code(request)
        # except Exception as e:
        #     transaction.rollback()
        #     return e
  

def execute_transaction_code(request):
    if type(request) != dict:
        request = request.dict(exclude_none = True)
    if request['preferred_shipping_line_ids']:
        request['preferred_shipping_line_ids'] = [uuid.UUID(str_id) for str_id in request['preferred_shipping_line_ids']]

    unique_object_params = get_unique_object_params(request)
    local_request = find_or_initialize(FclFreightRateLocalRequest, **unique_object_params)
   
    create_params = get_create_params(request)

    for key, value in create_params.items(): 
        setattr(local_request, key, value) 

    if local_request.validate():
        local_request.save()

    create_audit(request, local_request.id)

    # local_request.delay(queue: 'low').send_notifications_to_supply_agents
    
    return {
    'id': local_request.id
    }

def get_unique_object_params(request):
    return {
    'source': request['source'],
    'source_id': request['source_id'],
    'performed_by_id': request['performed_by_id'],
    'performed_by_type': request['performed_by_type'],
    'performed_by_org_id': request['performed_by_org_id']
    }
  
def get_create_params(request):
    return {key:value for key,value in request.items() if key not in ['source','source_id','performed_by_id','performed_by_type','performed_by_org_id']} | ({'status': 'active'})
  
def create_audit(request, local_request_id):
    request['cargo_readiness_date'] = request['cargo_readiness_date'].isoformat()

    if request['preferred_shipping_line_ids']:
        request['preferred_shipping_line_ids'] = [str(str_id) for str_id in request['preferred_shipping_line_ids']]

    FclFreightRateAudit.create(
        action_name = 'create',
        performed_by_id = request['performed_by_id'],
        data = {key:value for key,value in request.items() if key != 'performed_by_id'},
        object_id = local_request_id,
        object_type = 'FclFreightRateLocalRequest'
    )