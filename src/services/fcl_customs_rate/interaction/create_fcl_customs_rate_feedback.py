from services.fcl_customs_rate.models.fcl_customs_rate import FclCustomsRate
from services.fcl_customs_rate.models.fcl_customs_rate_audit import FclCustomsRateAudit
from services.fcl_customs_rate.models.fcl_customs_rate_feedback import FclCustomsRateFeedback
from libs.get_multiple_service_objects import get_multiple_service_objects
from fastapi import HTTPException
from database.db_migration import db
from services.fcl_customs_rate.interaction.create_fcl_customs_rate_job import (
    create_fcl_customs_rate_job,
)
def create_fcl_customs_rate_feedback(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    rate = FclCustomsRate.select(FclCustomsRate.id).where(FclCustomsRate.id == request.get('rate_id')).first()

    if not rate:
        raise HTTPException(status_code=400, detail='Rate not found')

    params = {
        'fcl_customs_rate_id': request.get('rate_id'),
        'source': request.get('source'),
        'source_id': request.get('source_id'),
        'performed_by_id': request.get('performed_by_id'),
        'performed_by_type': request.get('performed_by_type'),
        'performed_by_org_id': request.get('performed_by_org_id')
    }

    customs_feedback = FclCustomsRateFeedback.select().where(
        FclCustomsRateFeedback.fcl_customs_rate_id == request.get('rate_id'),
        FclCustomsRateFeedback.source == request.get('source'),
        FclCustomsRateFeedback.source_id == request.get('source_id'),
        FclCustomsRateFeedback.performed_by_id == request.get('performed_by_id'),
        FclCustomsRateFeedback.performed_by_type == request.get('performed_by_type'),
        FclCustomsRateFeedback.performed_by_org_id == request.get('performed_by_org_id'),
        FclCustomsRateFeedback.status == 'active').first()

    if not customs_feedback:
        customs_feedback = FclCustomsRateFeedback(**params)
        next_sequence_value = db.execute_sql("SELECT nextval('fcl_customs_rate_feedback_serial_id_seq'::regclass)").fetchone()[0]
        setattr(customs_feedback,'serial_id',next_sequence_value)

    create_params = get_create_params(request)
    for attr, value in create_params.items():
        setattr(customs_feedback, attr, value)
    
    customs_feedback.set_location()
    customs_feedback.set_spot_search()
    if customs_feedback.feedbacks:
        feedbacks = customs_feedback.feedbacks + request.get('feedbacks')
        customs_feedback.feedbacks = list(set(feedbacks))
    else:
        customs_feedback.feedbacks = request.get('feedbacks')
    
    if customs_feedback.remarks:
        remarks = customs_feedback.remarks + request.get('remarks')
        customs_feedback.remarks = list(set(remarks))
    else:
        customs_feedback.remarks = request.get('remarks')
    try:
        customs_feedback.save()
    except:
        raise HTTPException(status_code=500, detail='Feedback did not Save')

    create_audit(request, customs_feedback)
    get_multiple_service_objects(customs_feedback)

    if customs_feedback.feedback_type == 'disliked':
        request['source_id'] = customs_feedback.id
        create_fcl_customs_rate_job(request, "rate_feedback")
        
    return {
      'id': customs_feedback.id,
      'serial_id':customs_feedback.serial_id
    }

def get_create_params(request):
    return {
        # 'feedbacks': request.get('feedbacks'),
        # 'remarks': request.get('remarks'),
        'preferred_customs_rate': request.get('preferred_customs_rate'),
        'preferred_customs_rate_currency': request.get('preferred_customs_rate_currency'),
        'feedback_type': request.get('feedback_type'),
        'booking_params': request.get('booking_params'),
        'status': 'active',
        'port_id':request.get('port_id'),
        'country_id':request.get('country_id'),
        'trade_type':request.get('trade_type'),
        'trade_id':request.get('trade_id'),
        'commodity': request.get('commodity'),
        'service_provider_id': request.get('service_provider_id'),
        'cargo_handling_type' : request.get('cargo_handling_type'),
        'spot_search_serial_id':request.get('spot_search_serial_id')

    }

def create_audit(request, customs_feedback):
    FclCustomsRateAudit.create(
        data = {key:value for key,value in request.items() if key != 'performed_by_id'},
        object_id = customs_feedback.id,
        object_type = 'FclCustomsRateFeedback',
        action_name = 'create',
        performed_by_id = request.get('performed_by_id')
    )