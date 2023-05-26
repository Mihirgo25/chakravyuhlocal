from services.fcl_customs_rate.models.fcl_customs_rate import FclCustomsRate
from services.fcl_customs_rate.models.fcl_customs_rate_audit import FclCustomsRateAudit
from services.fcl_customs_rate.models.fcl_customs_rate_feedback import FclCustomsRateFeedback
from celery_worker import update_multiple_service_objects
from datetime import datetime
from fastapi import HTTPException
from database.db_migration import db

def create_fcl_customs_rate_feedback(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    rate = FclCustomsRate.select().where(FclCustomsRate.id == request.get('rate_id')).first()

    if not rate:
        raise HTTPException(status_code=400, detail='Rate is invalid')

    params = {
        'fcl_customs_rate_id': request.get('rate_id'),
        'source': request.get('source'),
        'source_id': request.get('source_id'),
        'performed_by_id': request.get('performed_by_id'),
        'performed_by_type': request.get('performed_by_type'),
        'performed_by_org_id': request.get('performed_by_org_id')
    }

    customs_feedback = FclCustomsRateFeedback.select().where(
        FclCustomsRateFeedback.fcl_customs_rate_id == request['rate_id'],
        FclCustomsRateFeedback.source == request['source'],
        FclCustomsRateFeedback.source_id == request['source_id'],
        FclCustomsRateFeedback.performed_by_id == request['performed_by_id'],
        FclCustomsRateFeedback.performed_by_type == request['performed_by_type'],
        FclCustomsRateFeedback.performed_by_org_id == request['performed_by_org_id']).first()

    if not customs_feedback:
        customs_feedback = FclCustomsRateFeedback(**params)

    create_params = get_create_params(request)
    for attr, value in create_params.items():
        setattr(customs_feedback, attr, value)

    try:
        customs_feedback.save()
    except:
        raise

    create_audit(request, customs_feedback)
    update_multiple_service_objects.apply_async(kwargs={'object':customs_feedback},queue='low')

    create_audit(request)

    return {
      'id': request.get('rate_id')
    }

def get_create_params(request):
    params = {
    'feedbacks': request.get('feedbacks'),
    'remarks': request.get('remarks'),
    'preferred_customs_rate': request.get('preferred_customs_rate'),
    'preferred_customs_rate_currency': request.get('preferred_customs_rate_currency'),
    'feedback_type': request.get('feedback_type'),
    'booking_params': request.get('booking_params'),
    'status': 'active'
    }

    return params

def create_audit(request, customs_feedback):
    FclCustomsRateAudit.create(
        created_at = datetime.now(),
        updated_at = datetime.now(),
        data = {key:value for key,value in request.items() if key != 'performed_by_id'},
        object_id = customs_feedback.id,
        object_type = 'FclFreightRateFeedback',
        action_name = 'create',
        performed_by_id = request.get('performed_by_id')
    )