from services.fcl_cfs_rate.models.fcl_cfs_rate import FclCfsRate
from services.fcl_cfs_rate.models.fcl_cfs_rate_audit import FclCfsRateAudit
from services.fcl_cfs_rate.models.fcl_cfs_rate_feedback import FclCfsRateFeedback
from libs.get_multiple_service_objects import get_multiple_service_objects
from fastapi import HTTPException
from database.db_migration import db
from services.fcl_cfs_rate.fcl_cfs_celery_worker import send_notifications_to_supply_agents_cfs_feedback_delay

def create_fcl_cfs_rate_feedback(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    rate = FclCfsRate.select(FclCfsRate.id).where(FclCfsRate.id == request.get('rate_id')).first()

    if not rate:
        raise HTTPException(status_code=404, detail='Rate not found')

    params = {
        'fcl_cfs_rate_id': request.get('rate_id'),
        'source': request.get('source'),
        'source_id': request.get('source_id'),
        'performed_by_id': request.get('performed_by_id'),
        'performed_by_type': request.get('performed_by_type'),
        'performed_by_org_id': request.get('performed_by_org_id')
    }

    cfs_feedback = FclCfsRateFeedback.select().where(
        FclCfsRateFeedback.fcl_cfs_rate_id == request.get('rate_id'),
        FclCfsRateFeedback.source == request.get('source'),
        FclCfsRateFeedback.source_id == request.get('source_id'),
        FclCfsRateFeedback.performed_by_id == request.get('performed_by_id'),
        FclCfsRateFeedback.performed_by_type == request.get('performed_by_type'),
        FclCfsRateFeedback.performed_by_org_id == request.get('performed_by_org_id')).first()

    if not cfs_feedback:
        cfs_feedback = FclCfsRateFeedback(**params)

    create_params = get_create_params(request)
    for attr, value in create_params.items():
        setattr(cfs_feedback, attr, value)
    
    cfs_feedback.set_port()
    cfs_feedback.set_spot_search()

    try:
        cfs_feedback.save()
    except:
        raise HTTPException(status_code=500, detail='Feedback did not Save')

    create_audit(request, cfs_feedback)
    get_multiple_service_objects(cfs_feedback)
    send_notifications_to_supply_agents_cfs_feedback_delay.apply_async(kwargs = {'object':cfs_feedback, 'request':request}, queue = 'low')

    return {
      'id': request.get('rate_id')
    }

def get_create_params(request):
    return {
        'feedbacks': request.get('feedbacks'),
        'remarks': request.get('remarks'),
        'preferred_rate': request.get('preferred_rate'),
        'preferred_rate_currency': request.get('preferred_rate_currency'),
        'feedback_type': request.get('feedback_type'),
        'booking_params': request.get('booking_params'),
        'status': 'active',
        'port_id':request.get('port_id'),
        'country_id':request.get('country_id'),
        'trade_type':request.get('trade_type'),
        'trade_id':request.get('trade_id'),
        'commodity': request.get('commodity'),
        'service_provider_id': request.get('service_provider_id')
    }

def create_audit(request, cfs_feedback):
    FclCfsRateAudit.create(
        data = {key:value for key,value in request.items() if key != 'performed_by_id'},
        object_id = cfs_feedback.id,
        object_type = 'FclCfsRateFeedback',
        action_name = 'create',
        performed_by_id = request.get('performed_by_id')
    )