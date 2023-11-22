from services.haulage_freight_rate.models.haulage_freight_rate_feedback import HaulageFreightRateFeedback
from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
from services.haulage_freight_rate.models.haulage_freight_rate_audit import HaulageFreightRateAudit
from fastapi import HTTPException
from database.db_session import db
from fastapi.encoders import jsonable_encoder
from libs.get_multiple_service_objects import get_multiple_service_objects
from micro_services.client import maps
from services.haulage_freight_rate.interactions.create_haulage_freight_rate_job import (
    create_haulage_freight_rate_job,
)


def create_haulage_freight_rate_feedback(request):
    with db.atomic():
        return execute_transaction_code(request)
    
def execute_transaction_code(request):
    """
    Create Haulage freight rate feedback
    Response Format:
        {"id": created_rate_id}
    """

    rate = HaulageFreightRate.select().where(HaulageFreightRate.id == request['haulage_freight_rate_id']).first()

    if not rate:
        raise HTTPException(status_code=400, detail='{} is invalid'.format(request['haulage_freight_rate_id']))
    
    row  = {
        'status': 'active',
        'haulage_freight_rate_id': request['haulage_freight_rate_id'],
        'source': request['source'],
        'source_id': request['source_id'],
        'performed_by_id': request['performed_by_id'],
        'performed_by_type': request['performed_by_type'],
        'performed_by_org_id': request['performed_by_org_id'],
        'transport_mode': request['transport_mode'],
    }

    feedback = HaulageFreightRateFeedback.select().where(
        HaulageFreightRateFeedback.status == 'active',
        HaulageFreightRateFeedback.haulage_freight_rate_id == request['haulage_freight_rate_id'],
        HaulageFreightRateFeedback.source == request['source'],
        HaulageFreightRateFeedback.source_id == request['source_id'],
        HaulageFreightRateFeedback.performed_by_id == request['performed_by_id'],
        HaulageFreightRateFeedback.performed_by_type == request['performed_by_type'],
        HaulageFreightRateFeedback.transport_mode == request['transport_mode'],
        HaulageFreightRateFeedback.performed_by_org_id == request['performed_by_org_id'],
        HaulageFreightRateFeedback.status == 'active').first()
    
    if not feedback:
        feedback = HaulageFreightRateFeedback(**row)
        next_sequence_value = db.execute_sql("SELECT nextval('haulage_freight_rate_feedback_serial_id_seq'::regclass)").fetchone()[0]
        setattr(feedback,'serial_id',next_sequence_value)

    create_params = get_create_params(request)

    for attr, value in create_params.items():
        setattr(feedback, attr, value)
    if feedback.feedbacks:
        feedbacks = feedback.feedbacks + request.get('feedbacks')
        feedback.feedbacks = list(set(feedbacks))
    else:
        feedback.feedbacks = request.get('feedbacks')
    
    if feedback.remarks:
        remarks = feedback.remarks + request.get('remarks')
        feedback.remarks = list(set(remarks))
    else:
        feedback.remarks = request.get('remarks')
    feedback.validate_before_save()
    try:
        feedback.save()
    except:
        raise HTTPException(status_code=400, detail='Feedback could not be saved')

    create_audit(request)
    get_multiple_service_objects(feedback)

    if feedback.feedback_type == 'disliked':
        request['source_id'] = feedback.id    
        create_haulage_freight_rate_job(request, "rate_feedback")
        
    return {'id': feedback.id, 'serial_id':feedback.serial_id}

 
def get_create_params(request):
    params = {
        # 'feedbacks': request.get('feedbacks'),
        # 'remarks': request.get('remarks'),
        'preferred_freight_rate': request.get('preferred_freight_rate'),
        'preferred_freight_rate_currency': request.get('preferred_freight_rate_currency'),
        'feedback_type': request.get('feedback_type'),
        'booking_params': request.get('booking_params'),
        'origin_location_id': request.get('origin_location_id'),
        'origin_city_id': request.get('origin_city_id'),
        'origin_country_id': request.get('origin_country_id'),
        'destination_location_id':request.get('destination_location_id'),
        'destination_city_id': request.get('destination_city_id'),
        'destination_country_id': request.get('destination_country_id'),
        'origin_location': request.get('origin_location'),
        'destination_location': request.get('destination_location'),
        'service_provider_id': request.get('service_provider_id'),
        'container_type': request.get('container_type'),
        'container_size': request.get('container_size'),
        'commodity': request.get('commodity'),
        'trailer_type': request.get('trailer_type'),
        'haulage_type': request.get('haulage_type'),
        'trip_type': request.get('trip_type'),
        'transport_mode': request.get('transport_mode'),
        'spot_search_serial_id':request.get('spot_search_serial_id')

    }
    loc_ids = []

    if request.get('origin_location_id'):
        loc_ids.append(request.get('origin_location_id'))
    if request.get('destination_location_id'):
        loc_ids.append(request.get('destination_location_id'))
    
    obj = {'filters':{"id": loc_ids }, 'includes': {'id': True, 'name': True, 'type': True, 'is_icd': True, 'cluster_id': True, 'city_id': True, 'country_id':True, 'country_code': True, 'display_name': True, 'default_params_required': True}}
    locations = maps.list_locations(obj)['list']
    locations_hash = {}
    for loc in locations:
        locations_hash[loc['id']] = loc
    if request.get('origin_location_id'):
        params['origin_location'] = locations_hash[request.get('origin_location_id')]
    if request.get('destination_location_id'):
        params['destination_location'] = locations_hash[request.get('destination_location_id')]
    return params
    
def create_audit(request):
    request = jsonable_encoder(request)
    audit_data = {key:value for key,value in request.items() if key != 'performed_by_id'}

    if request.get("transport_mode") == 'trailer':
        object_type="TrailerFreightRateFeedback"
    else:
        object_type="HaulageFreightRateFeedback"

    HaulageFreightRateAudit.create(
        action_name = 'create',
        performed_by_id = request['performed_by_id'],
        data = audit_data,
        object_type = object_type,
        sourced_by_id = request.get('sourced_by_id'),
        procured_by_id = request.get('procured_by_id')
    )



    
