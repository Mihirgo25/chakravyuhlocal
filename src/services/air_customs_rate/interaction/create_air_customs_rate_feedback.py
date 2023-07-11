from services.air_customs_rate.models.air_customs_rate import AirCustomsRate
from services.air_customs_rate.models.air_customs_rate_audit import AirCustomsRateAudit
from services.air_customs_rate.models.air_customs_rate_feedback import AirCustomsRateFeedback
from celery_worker import update_multiple_service_objects
from fastapi import HTTPException
from database.db_migration import db

def create_air_customs_rate_feedback(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    rate = AirCustomsRate.select(AirCustomsRate.id).where(AirCustomsRate.id == request.get('rate_id')).first()

    if not rate:
        raise HTTPException(status_code=400, detail='Rate is invalid')

    params = {
        'air_customs_rate_id': request.get('rate_id'),
        'source': request.get('source'),
        'source_id': request.get('source_id'),
        'performed_by_id': request.get('performed_by_id'),
        'performed_by_type': request.get('performed_by_type'),
        'performed_by_org_id': request.get('performed_by_org_id')
    }

    air_customs_feedback = AirCustomsRateFeedback.select().where(
        AirCustomsRateFeedback.air_customs_rate_id == request.get('rate_id'),
        AirCustomsRateFeedback.source == request.get('source'),
        AirCustomsRateFeedback.source_id == request.get('source_id'),
        AirCustomsRateFeedback.performed_by_id == request.get('performed_by_id'),
        AirCustomsRateFeedback.performed_by_type == request.get('performed_by_type'),
        AirCustomsRateFeedback.performed_by_org_id == request.get('performed_by_org_id')).first()

    if not air_customs_feedback:
        air_customs_feedback = AirCustomsRateFeedback(**params)

    create_params = get_create_params(request)
    for attr, value in create_params.items():
        setattr(air_customs_feedback, attr, value)
    
    air_customs_feedback.set_airport()
    air_customs_feedback.set_spot_search()

    try:
        air_customs_feedback.save()
    except:
        raise HTTPException(status_code=500, detail='Feedback did not Save')

    create_audit(request, air_customs_feedback.id)
    update_multiple_service_objects.apply_async(kwargs={'object':air_customs_feedback},queue='low')

    return {
      'id': request.get('rate_id')
    }

def get_create_params(request):
    return {
        'feedbacks': request.get('feedbacks'),
        'remarks': request.get('remarks'),
        'preferred_customs_rate': request.get('preferred_customs_rate'),
        'preferred_customs_rate_currency': request.get('preferred_customs_rate_currency'),
        'feedback_type': request.get('feedback_type'),
        'booking_params': request.get('booking_params'),
        'status': 'active',
        'airport_id':request.get('airport_id'),
        'country_id':request.get('country_id'),
        'trade_type':request.get('trade_type'),
        'trade_id':request.get('trade_id'),
        'commodity': request.get('commodity'),
        'service_provider_id': request.get('service_provider_id'),
        'continent_id':request.get('continent_id'),
        'city_id':request.get('city_id')
    }

def create_audit(request, air_customs_feedback_id):
    data = {key:value for key,value in request.items() if key != 'performed_by_id'}
    AirCustomsRateAudit.create(
        data = data,
        object_id = air_customs_feedback_id,
        object_type = 'AirCustomsRateFeedback',
        action_name = 'create',
        performed_by_id = request.get('performed_by_id')
    )