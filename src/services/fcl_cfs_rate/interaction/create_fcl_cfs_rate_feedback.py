from services.fcl_cfs_rate.models.fcl_cfs_rate import FclCfsRate
from services.fcl_cfs_rate.models.fcl_cfs_rate_audit import FclCfsRateAudit
from services.fcl_cfs_rate.models.fcl_cfs_rate_feedback import FclCfsRateFeedback
from libs.get_multiple_service_objects import get_multiple_service_objects
from fastapi import HTTPException
from database.db_migration import db
from services.fcl_cfs_rate.fcl_cfs_celery_worker import send_notifications_to_supply_agents_cfs_feedback_delay
from services.fcl_cfs_rate.interaction.create_fcl_cfs_rate_job import create_fcl_cfs_rate_job

def create_fcl_cfs_rate_feedback(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    rate = FclCfsRate.select(FclCfsRate.id).where(FclCfsRate.id == request.get('rate_id')).first()

    if not rate:
        raise HTTPException(status_code=400, detail='CFS Rate not found')

    params = {
        'fcl_cfs_rate_id': request.get('rate_id'),
        'source': request.get('source'),
        'source_id': request.get('source_id'),
        'performed_by_id': request.get('performed_by_id'),
        'performed_by_type': request.get('performed_by_type'),
        'performed_by_org_id': request.get('performed_by_org_id'),
        'trade_type':request.get('trade_type')
    }

    cfs_feedback = FclCfsRateFeedback.select().where(
        FclCfsRateFeedback.fcl_cfs_rate_id == request.get('rate_id'),
        FclCfsRateFeedback.source == request.get('source'),
        FclCfsRateFeedback.source_id == request.get('source_id'),
        FclCfsRateFeedback.performed_by_id == request.get('performed_by_id'),
        FclCfsRateFeedback.performed_by_type == request.get('performed_by_type'),
        FclCfsRateFeedback.performed_by_org_id == request.get('performed_by_org_id'),
        FclCfsRateFeedback.status == 'active',
        FclCfsRateFeedback.trade_type == request.get('trade_type')).first()

    if not cfs_feedback:
        cfs_feedback = FclCfsRateFeedback(**params)
        next_sequence_value = db.execute_sql("SELECT nextval('fcl_cfs_rate_feedback_serial_id_seq'::regclass)").fetchone()[0]
        setattr(cfs_feedback,'serial_id',next_sequence_value)

    create_params = get_create_params(request)
    for attr, value in create_params.items():
        setattr(cfs_feedback, attr, value)
    
    cfs_feedback.feedbacks = list(set(cfs_feedback.feedbacks + request.get('feedbacks',[]))) if cfs_feedback.feedbacks else request.get('feedbacks',[])
    cfs_feedback.remarks = list(set(cfs_feedback.feedbacks + request.get('remarks',[]))) if cfs_feedback.remarks else request.get('remarks',[])
    cfs_feedback.attachment_file_urls = list(set(cfs_feedback.attachment_file_urls + request.get('attachment_file_urls',[]))) if cfs_feedback.attachment_file_urls else request.get('attachment_file_urls',[])

    cfs_feedback.set_port()
    cfs_feedback.set_spot_search()

    try:
        cfs_feedback.save()
    except:
        raise HTTPException(status_code=500, detail='Feedback did not Save')

    create_audit(request, cfs_feedback)
    get_multiple_service_objects(cfs_feedback)
    send_notifications_to_supply_agents_cfs_feedback_delay.apply_async(kwargs = {'object':cfs_feedback, 'request':request}, queue = 'low')

    if cfs_feedback.feedback_type == 'disliked':
        request['source_id'] = cfs_feedback.id
        request['serial_id'] = cfs_feedback.serial_id
        create_fcl_cfs_rate_job(request, "rate_feedback")

    return {
      'id': cfs_feedback.id,
      'serial_id':cfs_feedback.serial_id
    }

def get_create_params(request):
    return {
        'preferred_rate': request.get('preferred_rate'),
        'preferred_rate_currency': request.get('preferred_rate_currency'),
        'feedback_type': request.get('feedback_type'),
        'booking_params': request.get('booking_params'),
        'status': 'active',
        'port_id':request.get('port_id'),
        'country_id':request.get('country_id'),
        'trade_id':request.get('trade_id'),
        'commodity': request.get('commodity'),
        'service_provider_id': request.get('service_provider_id'),
        'spot_search_serial_id':request.get('spot_search_serial_id'),
        'cogo_entity_id':request.get('cogo_entity_id')
    }

def create_audit(request, cfs_feedback):
    FclCfsRateAudit.create(
        data = {key:value for key,value in request.items() if key != 'performed_by_id'},
        object_id = cfs_feedback.id,
        object_type = 'FclCfsRateFeedback',
        action_name = 'create',
        performed_by_id = request.get('performed_by_id')
    )