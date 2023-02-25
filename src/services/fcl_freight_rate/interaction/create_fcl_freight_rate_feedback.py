from database.db_session import db
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback

def create_fcl_freight_rate_feedback(request):
    with db.atomic() as transaction:
        try:
            rate = FclFreightRate.find(request['rate_id'])

            # if rate:
            #     request['errors.add(:rate_id, 'is invalid') 
            #     return

            feedback, created = FclFreightRateFeedback.get_or_create(**get_object_unique_params(request))
            feedback.set_attrs(**get_create_params(request))
            feedback.save()

            if not feedback.save():
                errors.merge!(feedback.errors)
                return 

            feedback.audits.create!(get_audit_params)

            update_likes_dislikes_count(rate, request)
            if request['feedback_type'] == 'disliked'
                feedback.delay(queue: 'low').send_create_notifications_to_supply_agents

            return {'id': request['rate_id']}

        except:
            transaction.rollback()
            return "Creation Failed"


def update_likes_dislikes_count(rate, request):
    validities = rate.validities

    validity = validities.select { |validity| validity[:id] == request['validity_id'] }.first
    if not validity:
        return None

    validity['likes_count'] = int(validity['likes_count']) + request['likes_count']
    validity['dislikes_count'] = int(validity['dislikes_count'])+ request['dislikes_count']

    rate.validities = validities

    rate.save!(validate: false)


def get_object_unique_params(request):
    params =  {
    'fcl_freight_rate_id': request['rate_id'],
    'validity_id': request['validity_id'],
    'source': request['source'],
    'source_id': request['source_id'],
    'performed_by_id': request['performed_by_id'],
    'performed_by_type': request['performed_by_type'],
    'performed_by_org_id': request['performed_by_org_id']
    }
    return params

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

def get_audit_params(request):
    return {
      'action_name': 'create',
      'performed_by_id': request['performed_by_id'],
      'data': {key:value for key,value in request if key != 'performed_by_id'}
    }