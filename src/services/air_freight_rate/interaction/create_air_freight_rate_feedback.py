from datetime import datetime
import time 
from database.db_session import db 
from playhouse.postgres_ext import *
from fastapi import HTTPException
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.models.air_freight_rate_feedback import AirFreightRateFeedbacks
from services.air_freight_rate.models.air_services_audit import AirServiceAudit
from celery_worker import update_multiple_service_objects
from celery_worker import send_create_notifications_to_supply_agents_function
from micro_services.client import *

def create_audit(request,feedback_id):
    AirServiceAudit.create(
        created_at=datetime.now(),
        updated_at=datetime.now(),
        data={key:value for key , value in request.items() if key != 'performed_by_id'},
        object_id=feedback_id,
        object_type='AirFreightRateFeedbacks',
        action_name='create',
        performed_by_id=request['performed_by_id']
        )

def create_air_freight_rate_feeback(request):
    object_type='Air_Freight_Rate_Feedbacks'
    query="create table if not exists air_services_audits{} partition of air_services_audits for values in ('{}')".format(object_type.lower(),object_type.replace("_",""))
    db.execute_sql(query)
    with db.atomic():
        return execute_transaction_code(request)
     
def execute_transaction_code(request):
    start = time.time()
    rate=AirFreightRate.select().where(AirFreightRate.id==request['rate_id']).first()
    if not rate:
        raise HTTPException (status_code=500, detail='Rate Id is invalid')
    
    row={
      'air_freight_rate_id': request['rate_id'],
      'validity_id': request['validity_id'],
      'source': request['source'],
      'source_id': request['source_id'],
      'performed_by_id': request['performed_by_id'],
      'performed_by_type': request['performed_by_type'],
      'performed_by_org_id': request['performed_by_org_id'],
      'trade_type':request['trade_type']
    }
    feedback=AirFreightRateFeedbacks.select().where(
        AirFreightRateFeedbacks.air_freight_rate_id==request.get('air_freight_rate_id'),
        AirFreightRateFeedbacks.validity_id==request.get('validity_id'),
        AirFreightRateFeedbacks.source==request.get('source'),
        AirFreightRateFeedbacks.source_id==request.get('source_id'),
        AirFreightRateFeedbacks.performed_by_id==request.get('performed_by_id'),
        AirFreightRateFeedbacks.performed_by_type==request.get('performed_by_type'),
        AirFreightRateFeedbacks.performed_by_org_id==request.get('performed_by_org_id')
    ).first()


    if not feedback:
        feedback=AirFreightRateFeedbacks(**row)

    create_params =get_create_params(request)

    for attr,value in create_params.items():
        if attr =='preffered_airline_ids' and value:
            ids=[]
            for val in value:
                ids.append(uuid.UUID(str(val)))
            setattr(feedback,attr,ids)
        else: 
            setattr(feedback,attr,value)
    feedback.validate_before_save()
    try:
        feedback.save()
    except:
        raise HTTPException(status_code= 400, detail="couldnt validate the object")
    
    create_audit(request,feedback.id)
    update_multiple_service_objects.apply_async(kwargs={'object':feedback},queue='low')

    update_likes_dislike_count(rate,request)

    if request['feedback_type']=='disliked':
        send_create_notifications_to_supply_agents_function.apply_async(kwargs={'object':feedback},queue='communication')

    end = time.time()
    print(end - start)
    return {'id': request['rate_id']}

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
    
def get_create_params(request):
    params={ 
        'feedbacks': request.get('feedbacks'),
        'remarks': request.get('remarks'),
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
        'weight':request.get('weight'),
        'volume':request.get('volume'),
        'packages_count':request.get('packages_count'),
        'operation_type':request.get('operation_type'),
        'status': 'active'
      }
    loc_ids=[]
    if request.get('origin_airport_id'):
        loc_ids.append(request.get('origin_airport_id'))
    if request.get('destination_airport_id'):
        loc_ids.append(request.get('destination_airport_id'))

    obj={'filters':{"id":loc_ids}}
    locations=maps.list_locations(obj)['list']
    locations_hash={}
    for loc in locations:
        locations_hash[loc['id']]=loc
    if request.get('origin_airport_id'):
        params['origin_airport']=locations_hash[request.get('origin_airport_id')]
    if request.get('destination_airport_id'):
        params['destination_airport']=locations_hash[request.get('destination_airport_id')]
    return params