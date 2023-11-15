from services.air_customs_rate.models.air_customs_rate import AirCustomsRate
from services.air_customs_rate.models.air_customs_rate_audit import AirCustomsRateAudit
from services.air_customs_rate.models.air_customs_rate_feedback import AirCustomsRateFeedback
from libs.get_multiple_service_objects import get_multiple_service_objects
from fastapi import HTTPException
from database.db_migration import db
from database.rails_db import get_partner_users_by_expertise, get_partner_users
from micro_services.client import maps
from celery_worker import create_communication_background
from services.air_customs_rate.interaction.create_air_customs_rate_job import (
    create_air_customs_rate_job
)
def create_air_customs_rate_feedback(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    rate = AirCustomsRate.select(AirCustomsRate.id).where(AirCustomsRate.id == request.get('rate_id')).first()

    if not rate:
        raise HTTPException(status_code=404, detail='Rate Not Found')

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
    if air_customs_feedback.feedbacks:
        air_customs_feedback.feedbacks = air_customs_feedback.feedbacks + request.get('feedbacks')
    else:
        air_customs_feedback.feedbacks = request.get('feedbacks')
    
    if air_customs_feedback.remarks:
        air_customs_feedback.remarks = air_customs_feedback.remarks + request.get('remarks')
    else:
        air_customs_feedback.remarks = request.get('remarks')
    try:
        air_customs_feedback.save()
    except:
        raise HTTPException(status_code=500, detail='Feedback did not Save')

    create_audit(request, air_customs_feedback.id)
    get_multiple_service_objects(air_customs_feedback)
    send_notifications_to_supply_agents(request)
    if air_customs_feedback.feedback_type == 'disliked':
        request['source_id'] = air_customs_feedback.id
        create_air_customs_rate_job(request, "rate_feedback")

    return {
      'id': air_customs_feedback.id,
      'serial_id':air_customs_feedback.serial_id
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

def supply_agents_to_notify(request):
    locations_data = AirCustomsRateFeedback.select(AirCustomsRateFeedback.airport_id, AirCustomsRateFeedback.country_id, AirCustomsRateFeedback.continent_id).where(AirCustomsRateFeedback.source_id == request.get('source_id')).dicts().get()
    locations = list(filter(None,[str(value or "") for key,value in locations_data.items()]))

    supply_agents_data = get_partner_users_by_expertise('air_customs', location_ids = locations, trade_type = request.get('trade_type'))
    supply_agents_list = list(set([item.get('partner_user_id') for item in supply_agents_data]))

    supply_agents_user_data = get_partner_users(supply_agents_list)
    supply_agents_user_ids = list(set([str(data['user_id']) for data in  supply_agents_user_data])) if supply_agents_user_data else None

    airport_ids = str(locations_data.get('airport_id') or '')

    route_data = []
    try:
        route_data = maps.list_locations({'filters':{'id':airport_ids}})['list']
    except Exception as e:
        print(e)

    route = {key['id']:key['display_name'] for key in route_data}
    return { 'user_ids': supply_agents_user_ids, 'location': route.get(str(locations_data.get('airport_id') or '')) }

def send_notifications_to_supply_agents(request):
    request_info = supply_agents_to_notify(request)
    data = {
        'type': 'platform_notification',
        'service': 'spot_search',
        'service_id': request.get('source_id'),
        'template_name': 'customs_rate_disliked',
        'variables': { 
            'service_type': 'air customs',
            'location': request_info.get('location'),
            'details':request.get('booking_params')
        }
    }
    for user_id in (request_info.get('user_ids') or []):
        data['user_id'] = user_id
        create_communication_background.apply_async(kwargs = {'data':data}, queue = 'low')