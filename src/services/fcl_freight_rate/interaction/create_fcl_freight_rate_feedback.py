from database.db_session import db
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
from datetime import datetime
from libs.logger import logger


def create_fcl_freight_rate_feedback(request):
    with db.atomic() as transaction:
        try:
            return execute_transaction_code(request)
        except Exception as e:
            transaction.rollback()
            return e

def execute_transaction_code(request):
    if type(request) != dict:
        request = request.__dict__

    rate = FclFreightRate.get(**{'id' :request['rate_id']})

    if not rate:
        raise Exception('{} is invalid'.format(request['rate_id']))

    row = {
        'fcl_freight_rate_id': request['rate_id'],
        'validity_id': request['validity_id'],
        'source': request['source'],
        'source_id': request['source_id'],
        'performed_by_id': request['performed_by_id'],
        'performed_by_type': request['performed_by_type'],
        'performed_by_org_id': request['performed_by_org_id']
    }

    feedback = FclFreightRateFeedback.select().where(
        FclFreightRateFeedback.fcl_freight_rate_id == request['rate_id'],
        FclFreightRateFeedback.validity_id == request['validity_id'],
        FclFreightRateFeedback.source == request['source'],
        FclFreightRateFeedback.source_id == request['source_id'],
        FclFreightRateFeedback.performed_by_id == request['performed_by_id'],
        FclFreightRateFeedback.performed_by_type == request['performed_by_type'],
        FclFreightRateFeedback.performed_by_org_id == request['performed_by_org_id']).first()

    if not feedback:
        feedback = FclFreightRateFeedback(**row)
        
    create_params = get_create_params(request)

    for attr, value in create_params.items():
        setattr(feedback, attr, value)

    try:
        if feedback.validate_before_save():
            feedback.save()

    except Exception as e:
        logger.error(e, exc_info=True)
        return e

    create_audit(request, feedback)

    update_likes_dislikes_count(rate, request)
    # if request['feedback_type'] == 'disliked':
        # return None
        # feedback.delay(queue: 'low').send_create_notifications_to_supply_agents

    return {'id': request['rate_id']}

def update_likes_dislikes_count(rate, request):
    validities = rate.validities
    validity = [validity_object for validity_object in validities if validity_object['id'] == request['validity_id']]
    if validity:
        validity = validity[0]
    else:
        return None

    validity['likes_count'] = int(validity['likes_count']) + request['likes_count']
    validity['dislikes_count'] = int(validity['dislikes_count'])+ request['dislikes_count']

    rate.validities = validities

    rate.save()

def get_create_params(request):
    params =  {
        'feedbacks': request['feedbacks'],
        'remarks': request['remarks'],
        'preferred_freight_rate': request['preferred_freight_rate'],
        'preferred_freight_rate_currency': request['preferred_freight_rate_currency'],
        'preferred_detention_free_days': request['preferred_detention_free_days'],
        'preferred_shipping_line_ids': request['preferred_shipping_line_ids'],
        'feedback_type': request['feedback_type'],
        'booking_params': request['booking_params'],
        'status': 'active'
    }
    return params


def create_audit(request, feedback):
    FclFreightRateAudit.create( 
        created_at = datetime.now(),
        updated_at = datetime.now(),
        data = {key:value for key,value in request.items() if key != 'performed_by_id'},
        object_id = feedback.id,
        object_type = 'FclFreightRateFeedback',
        action_name = 'create',
        performed_by_id = request['performed_by_id']
    )