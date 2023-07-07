
from services.haulage_freight_rate.models.haulage_freight_rate_feedback import HaulageFreightRateFeedback
from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
from services.haulage_freight_rate.models.haulage_freight_rate_audit import HaulageFreightRateAudit
from fastapi import HTTPException
from database.db_session import db
from fastapi.encoders import jsonable_encoder
from celery_worker import update_multiple_service_objects


def create_haulage_freight_rate_feedback(request):
    with db.atomic():
        return execute_transaction_code(request)
    
def execute_transaction_code(request):
    """
    Create Haulage freight rate feedback
    Response Format:
        {"id": created_rate_id}
    """

    rate = HaulageFreightRate.select().where(HaulageFreightRate.id == request['rate_id']).first()

    if not rate:
        raise HTTPException(status_code=400, detail='{} is invalid'.format(request['rate_id']))
    
    row  = {
        'status': 'active',
        'haulage_freight_rate_id': request['rate_id'],
        'source': request['source'],
        'source_id': request['source_id'],
        'performed_by_id': request['performed_by_id'],
        'performed_by_type': request['performed_by_type'],
        'performed_by_org_id': request['performed_by_org_id'],
    }

    feedback = HaulageFreightRateFeedback.select().where(
        HaulageFreightRateFeedback.status == 'active',
        HaulageFreightRateFeedback.haulage_freight_rate_id == request['rate_id'],
        HaulageFreightRateFeedback.source == request['source'],
        HaulageFreightRateFeedback.source_id == request['source_id'],
        HaulageFreightRateFeedback.performed_by_id == request['performed_by_id'],
        HaulageFreightRateFeedback.performed_by_type == request['performed_by_type'],
        HaulageFreightRateFeedback.performed_by_org_id == request['performed_by_org_id']).first()
    
    if not feedback:
        feedback = HaulageFreightRateFeedback(**row)

    create_params = get_create_params(request)

    for attr, value in create_params.items():
        setattr(feedback, attr, value)

    feedback.validate_before_save()
    try:
        feedback.save()
    except:
        raise HTTPException(status_code=400, detail='Feedback could not be saved')

    create_audit(request)
    update_multiple_service_objects.apply_async(kwargs={'object':feedback},queue='low')

    return {'id': request['rate_id']}


def get_create_params(request):
    params = {
        'feedbacks': request.get('feedbacks'),
        'remarks': request.get('remarks'),
        'preferred_freight_rate': request.get('preferred_freight_rate'),
        'preferred_freight_rate_currency': request.get('preferred_freight_rate_currency'),
        'feedback_type': request.get('feedback_type'),
        'booking_params': request.get('booking_params'),
    }
    return params
    
def create_audit(request):
    request = jsonable_encoder(request)
    audit_data = {key:value for key,value in request.items() if key != 'performed_by_id'}

    HaulageFreightRateAudit.create(
        action_name = 'create',
        performed_by_id = request['performed_by_id'],
        data = audit_data,
        object_type = 'HaulageFreightRateFeedback',
        sourced_by_id = request.get('sourced_by_id'),
        procured_by_id = request.get('procured_by_id')
    )



    
