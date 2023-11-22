from database.db_session import db
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
from datetime import datetime
from playhouse.postgres_ext import *
from celery_worker import send_create_notifications_to_supply_agents_function, set_relevant_supply_agents_function
from celery_worker import update_multiple_service_objects
from fastapi import HTTPException
from micro_services.client import *
from services.bramhastra.celery import send_feedback_statistics_in_delay
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_job import create_fcl_freight_rate_job



def create_fcl_freight_rate_feedback(request):
    object_type = 'Fcl_Freight_Rate_Feedback'
    query = "create table if not exists fcl_services_audits_{} partition of fcl_services_audits for values in ('{}')".format(object_type.lower(), object_type.replace("_",""))
    db.execute_sql(query)
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    action = 'update'
    
    rate = FclFreightRate.select().where(FclFreightRate.id == request['rate_id']).first()

    if not rate:
        raise HTTPException(status_code=400, detail='{} is invalid'.format(request['rate_id']))

    row = {
        'fcl_freight_rate_id': request['rate_id'],
        'validity_id': request['validity_id'],
        'source': request['source'],
        'source_id': request['source_id'],
        'performed_by_id': request['performed_by_id'],
        'performed_by_type': request['performed_by_type'],
        'performed_by_org_id': request['performed_by_org_id'],
        'origin_port_id':request['origin_port_id']
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
        action = 'create'
        feedback = FclFreightRateFeedback(**row)

    create_params = get_create_params(request)

    for attr, value in create_params.items():
        if attr == 'preferred_shipping_line_ids' and value:
            ids = []
            for val in value:
                ids.append(uuid.UUID(str(val)))
            setattr(feedback, attr, ids)
        else:
            setattr(feedback, attr, value)

    try:
        if feedback.validate_before_save():
            feedback.save()
    except:
        raise

    create_audit(request, feedback)
    update_multiple_service_objects.apply_async(kwargs={'object':feedback},queue='low')

    # update_likes_dislikes_count(rate, request)
    if request['feedback_type'] == 'disliked':
        set_relevant_supply_agents_function.apply_async(kwargs={'object':feedback,'request':request},queue='critical')
        request['source_id'] = feedback.id
        request['serial_id'] = feedback.serial_id
        create_fcl_freight_rate_job(request, "rate_feedback")
        
    send_feedback_statistics_in_delay.apply_async(kwargs = {'action': action,'feedback': feedback, 'request': request},queue = 'statistics')

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
        'feedbacks': request.get('feedbacks'),
        'remarks': request.get('remarks'),
        'preferred_freight_rate': request.get('preferred_freight_rate'),
        'preferred_freight_rate_currency': request.get('preferred_freight_rate_currency'),
        'preferred_detention_free_days': request.get('preferred_detention_free_days'),
        'preferred_shipping_line_ids': request.get('preferred_shipping_line_ids'),
        'feedback_type': request.get('feedback_type'),
        'booking_params': request.get('booking_params'),
        'status': 'active',
        'cogo_entity_id':request.get('cogo_entity_id'),
        'origin_continent_id':request.get('origin_continent_id'),
        'origin_port_id':request.get('origin_port_id'),
        'origin_trade_id': request.get('origin_trade_id'),
        'origin_country_id': request.get('origin_country_id'),
        'destination_port_id': request.get('destination_port_id'),
        'destination_continent_id': request.get('destination_continent_id'),
        'destination_trade_id': request.get('destination_trade_id'),
        'destination_country_id': request.get('destination_country_id'),
        'commodity': request.get('commodity'),
        'container_size': request.get('container_size'),
        'container_type': request.get('container_type'),
        'service_provider_id': request.get('service_provider_id'),
        'attachment_file_urls':request.get('attachment_file_urls'),
        'commodity_description':request.get('commodity_description'),
        'rate_type':request.get('rate_type') or request.get('booking_params', {}).get('rate_card', {}).get('rate_type')
    }
    loc_ids = []

    if request.get('origin_port_id'):
        loc_ids.append(request.get('origin_port_id'))
    if request.get('destination_port_id'):
        loc_ids.append(request.get('destination_port_id'))
    
    obj = {'filters':{"id": loc_ids }}
    locations = maps.list_locations(obj)['list']
    locations_hash = {}
    for loc in locations:
        locations_hash[loc['id']] = loc
    if request.get('origin_port_id'):
        params['origin_port'] = locations_hash[request.get('origin_port_id')]
    if request.get('destination_port_id'):
        params['destination_port'] = locations_hash[request.get('destination_port_id')]
    
    return params


def create_audit(request, feedback):
    FclServiceAudit.create(
        created_at = datetime.now(),
        updated_at = datetime.now(),
        data = {key:value for key,value in request.items() if key != 'performed_by_id'},
        object_id = feedback.id,
        object_type = 'FclFreightRateFeedback',
        action_name = 'create',
        performed_by_id = request['performed_by_id']
    )