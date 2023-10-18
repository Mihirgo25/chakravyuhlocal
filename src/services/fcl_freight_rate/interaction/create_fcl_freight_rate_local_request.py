from services.fcl_freight_rate.models.fcl_freight_rate_local_request import FclFreightRateLocalRequest
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
import uuid
from database.db_session import db
from celery_worker import send_notifications_to_supply_agents_local_request
from libs.get_multiple_service_objects import get_multiple_service_objects

def create_fcl_freight_rate_local_request(request):
    object_type = 'Fcl_Freight_Rate_Local_Request' 
    query = "create table if not exists fcl_services_audits_{} partition of fcl_services_audits for values in ('{}')".format(object_type.lower(), object_type.replace("_","")) 
    db.execute_sql(query)
    with db.atomic():
        return execute_transaction_code(request)
  

def execute_transaction_code(request):
    if type(request) != dict:
        request = request.dict(exclude_none = True)
    if request.get('preferred_shipping_line_ids'):
        request['preferred_shipping_line_ids'] = [uuid.UUID(str_id) for str_id in request['preferred_shipping_line_ids']]

    unique_object_params = {
        'source': request.get('source'),
        'source_id': request.get('source_id'),
        'performed_by_id': request.get('performed_by_id'),
        'performed_by_type': request.get('performed_by_type'),
        'performed_by_org_id': request.get('performed_by_org_id')
    }

    local_request = FclFreightRateLocalRequest.select().where(
        FclFreightRateLocalRequest.source == request.get('source'),
        FclFreightRateLocalRequest.source_id == request.get('source_id'),
        FclFreightRateLocalRequest.performed_by_id == request.get('performed_by_id'),
        FclFreightRateLocalRequest.performed_by_type == request.get('performed_by_type'),
        FclFreightRateLocalRequest.performed_by_org_id == request.get('performed_by_org_id') 
    ).first()

    if not local_request:
        local_request = FclFreightRateLocalRequest(**unique_object_params)
   
    create_params = get_create_params(request)

    for key, value in create_params.items(): 
        setattr(local_request, key, value) 

    if local_request.validate():
        local_request.save()

    create_audit(request, local_request.id)

    get_multiple_service_objects(local_request)

    send_notifications_to_supply_agents_local_request.apply_async(kwargs={'object':local_request},queue='communication')

    
    return {
    'id': local_request.id
    }

def get_create_params(request):
    return {key:value for key,value in request.items() if key not in ['source','source_id','performed_by_id','performed_by_type','performed_by_org_id']} | ({'status': 'active'})
  
def create_audit(request, local_request_id):
    if request.get('cargo_readiness_date'):
        request['cargo_readiness_date'] = request['cargo_readiness_date'].isoformat()

    if request.get('preferred_shipping_line_ids'):
        request['preferred_shipping_line_ids'] = [str(str_id) for str_id in request['preferred_shipping_line_ids']]

    FclServiceAudit.create(
        action_name = 'create',
        performed_by_id = request.get('performed_by_id'),
        data = {key:value for key,value in request.items() if key != 'performed_by_id'},
        object_id = local_request_id,
        object_type = 'FclFreightRateLocalRequest'
    )