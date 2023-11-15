from database.db_session import db
from services.air_freight_rate.models.air_freight_rate_local_feedback import AirFreightRateLocalFeedback
from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
from services.air_freight_rate.models.air_freight_rate_audit import AirFreightRateAudit
from celery_worker import send_notifications_to_supply_agents_local_feedback
from libs.get_multiple_service_objects import get_multiple_service_objects
from fastapi import HTTPException

def create_air_freight_rate_local_feedback(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    action_name = 'update'
    local_rate = AirFreightRateLocal.select(AirFreightRateLocal.id).where(AirFreightRateLocal.id == request.get('rate_id')).first()

    if not local_rate:
        return HTTPException(status_code=400, detail='Rate not found')

    locals_feedback = AirFreightRateLocalFeedback.select().where(
        AirFreightRateLocalFeedback.air_freight_rate_local_id == request.get('rate_id'),
        AirFreightRateLocalFeedback.source == request.get('source'),
        AirFreightRateLocalFeedback.source_id == request.get('source_id'),
        AirFreightRateLocalFeedback.performed_by_id == request.get('performed_by_id'),
        AirFreightRateLocalFeedback.performed_by_type == request.get('performed_by_type'),
        AirFreightRateLocalFeedback.performed_by_org_id == request.get('performed_by_org_id') 
    ).first()

    if not locals_feedback:
        action_name = 'create'
        unique_object_params = {
            'air_freight_rate_local_id':request.get('rate_id'),
            'source': request.get('source'),
            'source_id': request.get('source_id'),
            'performed_by_id': request.get('performed_by_id'),
            'performed_by_type': request.get('performed_by_type'),
            'performed_by_org_id': request.get('performed_by_org_id')
        }
        locals_feedback = AirFreightRateLocalFeedback(**unique_object_params)
    
    create_params = get_create_params(request)

    for key, value in create_params.items(): 
        setattr(locals_feedback, key, value) 

    try:
        locals_feedback.save()
    except:
        raise HTTPException(status_code=500, detail='Feedback did not Save')

    create_audit(request, locals_feedback.id, action_name)
    get_multiple_service_objects(locals_feedback)

    send_notifications_to_supply_agents_local_feedback.apply_async(kwargs={'object':locals_feedback},queue='communication')

    return {
        'id': locals_feedback.id,
        'serial_id':locals_feedback.serial_id
    }

def get_create_params(request):
    return {key:value for key,value in request.items() if key not in ['source','source_id','performed_by_id','performed_by_type','performed_by_org_id']} | ({'status': 'active'})

def create_audit(request, local_request_id, action_name):
    if request.get('preferred_airline_ids'):
        request['preferred_airline_ids'] = [str(str_id) for str_id in request['preferred_airline_ids']]

    AirFreightRateAudit.create(
        action_name = action_name,
        performed_by_id = request.get('performed_by_id'),
        data = {key:value for key,value in request.items() if key != 'performed_by_id'},
        object_id = local_request_id,
        object_type = 'AirFreightRateLocalFeedback'
    )