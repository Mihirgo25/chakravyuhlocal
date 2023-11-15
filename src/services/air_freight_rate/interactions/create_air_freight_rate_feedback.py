from datetime import datetime
from database.db_session import db 
from playhouse.postgres_ext import *
from fastapi import HTTPException
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.models.air_freight_rate_feedback import AirFreightRateFeedback
from services.air_freight_rate.models.air_services_audit import AirServiceAudit
from celery_worker import send_air_freight_rate_feedback_notification_in_delay,get_rate_from_cargo_ai_in_delay
from micro_services.client import *
from services.air_freight_rate.constants.air_freight_rate_constants import CARGOAI_ACTIVE_ON_DISLIKE_RATE
from libs.get_multiple_service_objects import get_multiple_service_objects
from services.air_freight_rate.interactions.create_air_freight_rate_job import create_air_freight_rate_job


def create_audit(request,feedback_id):
    AirServiceAudit.create(
        created_at=datetime.now(),
        updated_at=datetime.now(),
        data={key:value for key , value in request.items() if key != 'performed_by_id'},
        object_id=feedback_id,
        object_type='AirFreightRateFeedback',
        action_name='create',
        performed_by_id=request['performed_by_id']
        )

def create_air_freight_rate_feedback(request):
    object_type='Air_Freight_Rate_Feedback'
    query="create table if not exists air_services_audits_{} partition of air_services_audits for values in ('{}')".format(object_type.lower(),object_type.replace("_",""))
    db.execute_sql(query)
    with db.atomic():
        return execute_transaction_code(request)
     
def execute_transaction_code(request):

    rate=AirFreightRate.select(AirFreightRate.id,AirFreightRate.validities,AirFreightRate.origin_airport_id,AirFreightRate.destination_airport_id,AirFreightRate.commodity).where(AirFreightRate.id==request['rate_id']).first()
    if not rate:
        raise HTTPException(status_code=404, detail='Rate Not Found')
    
    row={
      'air_freight_rate_id': request['rate_id'],
      'validity_id': request['validity_id'],
      'source': request['source'],
      'source_id': request['source_id'],
      'performed_by_id': request['performed_by_id'],
      'performed_by_type': request['performed_by_type'],
      'performed_by_org_id': request['performed_by_org_id'],
    }
    feedback=AirFreightRateFeedback.select().where(
        AirFreightRateFeedback.air_freight_rate_id==request.get('air_freight_rate_id'),
        AirFreightRateFeedback.validity_id==request.get('validity_id'),
        AirFreightRateFeedback.source==request.get('source'),
        AirFreightRateFeedback.source_id==request.get('source_id'),
        AirFreightRateFeedback.performed_by_id==request.get('performed_by_id'),
        AirFreightRateFeedback.performed_by_type==request.get('performed_by_type'),
        AirFreightRateFeedback.performed_by_org_id==request.get('performed_by_org_id')
    ).first()


    if not feedback:
        feedback=AirFreightRateFeedback(**row)

    create_params =get_create_params(request,rate)

    for attr,value in create_params.items():
        if attr =='preferred_airline_ids' and value:
            ids=[]
            for val in value:
                ids.append(uuid.UUID(str(val)))
            setattr(feedback,attr,ids)
        else: 
            setattr(feedback,attr,value)
    if feedback.feedbacks:
        feedback.feedbacks = feedback.feedbacks + request.get('feedbacks')
    else:
        feedback.feedbacks = request.get('feedbacks')
    
    if feedback.remarks:
        feedback.remarks = feedback.remarks + request.get('remarks')
    else:
        feedback.remarks = request.get('remarks')
    feedback.validate_before_save()
    try:
        feedback.save()
    except:
        raise HTTPException(status_code= 400, detail = "Feedback Didn't Save")
    
    create_audit(request,feedback.id)
    
    get_multiple_service_objects(feedback)
    update_likes_dislike_count(rate,request)

    if request['feedback_type']=='disliked':
        if CARGOAI_ACTIVE_ON_DISLIKE_RATE:
            get_rate_from_cargo_ai_in_delay.apply_async(kwargs={'air_freight_rate':rate,'feedback':feedback,'performed_by_id':request.get('performed_by_id')},queue='critical')
        airports = get_locations(rate)
        if airports:
            send_air_freight_rate_feedback_notification_in_delay.apply_async(kwargs={'object':feedback,'air_freight_rate':rate,'airports':airports},queue='communication')
    
        request['source_id'] = feedback.id
        create_air_freight_rate_job(request, "rate_feedback")   
    
    return {
        'id': feedback.id,
        'serial_id':feedback.serial_id
        }

def update_likes_dislike_count(rate,request):
    validities=rate.validities
    validity=[validity_object for validity_object in validities if validity_object['id']==request.get('validity_id')]
    if validity:
        validity=validity[0]
    else:
        return None
    validity['likes_count']=int(validity['likes_count'])+request['likes_count']
    validity['dislikes_count']=int(validity['dislikes_count'])+request['dislikes_count']

    rate.validities=validities

    rate.save()
    
def get_create_params(request,rate):
    params={ 
        # 'feedbacks': request.get('feedbacks'),
        # 'remarks': request.get('remarks'),
        'preferred_freight_rate': request.get('preferred_freight_rate'),
        'preferred_freight_rate_currency': request.get('preferred_freight_rate_currency'),
        'preferred_storage_free_days': request.get('preferred_storage_free_days'),
        'preferred_airline_ids': request.get('preferred_airline_ids'),
        'feedback_type': request.get('feedback_type'),
        'booking_params': request.get('booking_params'),
        'trade_type': request.get('trade_type'),
        'origin_airport_id':request.get('origin_airport_id'),
        'origin_country_id':request.get('origin_country_id'),
        'origin_continent_id':request.get('origin_continent_id'),
        'origin_trade_id':request.get('origin_trade_id'),
        'destination_airport_id':request.get('destination_airport_id'),
        'destination_country_id':request.get('destination_country_id'),
        'destination_continent_id':request.get('destination_continent_id'),
        'destination_trade_id':request.get('destination_trade_id'),
        'commodity':request.get('commodity'),
        'cogo_entity_id':request.get('cogo_entity_id'),
        'service_provider_id':request.get('service_provider_id'),
        'operation_type':request.get('operation_type'),
        'status': 'active',
        'airline_id':request.get('airline_id')
      }
    return params

def get_locations(air_freight_rate):
    location_ids = [str(air_freight_rate.origin_airport_id), str(air_freight_rate.destination_airport_id)]
    locations = maps.list_locations({'filters': { 'id': location_ids }, 'pagination_data_required': False})['list']
    if locations[0]['id']==str(air_freight_rate.origin_airport_id):
        return locations
    destination = locations[0]
    return [locations[1],destination]