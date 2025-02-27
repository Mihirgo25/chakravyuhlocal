from fastapi import HTTPException
from datetime import * 
from peewee import * 
import json
from playhouse.postgres_ext import *
from database.db_session import db
from fastapi.encoders import jsonable_encoder
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.models.air_freight_rate_audit import AirFreightRateAudit
from services.air_freight_rate.models.air_freight_rate_validity import AirFreightRateValidity
from fastapi.encoders import jsonable_encoder
from configs.global_constants import SERVICE_PROVIDER_FF
from services.air_freight_rate.constants.air_freight_rate_constants import COGOXPRESS
from services.air_freight_rate.air_celery_worker import update_air_freight_rate_job_on_rate_addition_delay

def update_air_freight_rate(request):
      with db.atomic():
        return execute(request)

def execute(request):
    object=find_object(request)

    if not object:
        raise HTTPException(status_code=400,detail="id is invalid")
    
    validities=object.validities
    validity_object = {}
    for validity in validities:
        if validity['id']==request.get('validity_id'):
            if request.get('validity_start') and request.get('validity_end'):

                if validate_validity_object(request['validity_start'],request['validity_end']):
                    validity_start=request.get('validity_start')
                    validity_end=request.get('validity_end')
                    validity_id = None
            else:
                validity_start=datetime.strptime(validity.get('validity_start'),'%Y-%m-%d').date() 
                validity_end=datetime.strptime(validity.get('validity_end'),'%Y-%m-%d').date()
                validity_id = request.get("validity_id")
            density_ratio = request.get("density_ratio") or "1:{}".format(validity['min_density_weight'])
            
            object.set_validities(validity_start,validity_end,request.get("min_price") or validity['min_price'],
                                  validity['currency'],request.get('weight_slabs'),False,validity_id,validity['density_category'],density_ratio,
                                  validity['initial_volume'] or request.get('initial_volume'),request.get('initial_gross_weight') or validity['initial_gross_weight'],
                                  request.get('available_volume') or validity['available_volume'],request.get('available_gross_weight') or validity['available_gross_weight'],
                                  object.rate_type,request.get('likes_count') or validity['likes_count'],request.get('dislikes_count') or validity['dislikes_count']
                                  )
            validity_object = jsonable_encoder(validity)
            
    if request.get('weight_slabs'):
        object.weight_slabs = sorted(request.get('weight_slabs'), key=lambda x: x['lower_limit'])
            
    if request.get('length'):
        object.length = request.get('length') 

    if request.get('breadth'):
        object.breadth = request.get('breadth') 

    if request.get('height'):
        object.height = request.get('height')

    if request.get('maximum_weight'):
        object.maximum_weight = request.get('maximum_weight')


    object.maximum_weight = request.get('maximum_weight')
    object.validate_before_save()
    try:
        object.save()
    except Exception as e:
        print("Exception in saving freight rate", e)

    create_audit(request, object.id)

    if str(object.service_provider_id)== SERVICE_PROVIDER_FF and not request.get('extension_not_required'):
        extend_rate_fun(object,request,validity_object)
        
    send_stats(request,object)

    if str(object.service_provider_id) != COGOXPRESS:
        update_air_freight_rate_job_on_rate_addition_delay.apply_async(kwargs={'request': request, "id": object.id},queue='fcl_freight_rate')

    return {
        'id':object.id
    }

def extend_rate_fun(object,request,validity_object):
    from services.air_freight_rate.air_celery_worker import extend_air_freight_rates_in_delay
    validity_object['validity_start']=datetime.strptime(validity_object.get('validity_start'),'%Y-%m-%d')
    validity_object['validity_end']=datetime.strptime(validity_object.get('validity_end'),'%Y-%m-%d')
    rate = request | {
        'origin_airport_id':str(object.origin_airport_id),
        'destination_airport_id':str(object.destination_airport_id),
        'commodity':object.commodity,
        'commodity_type':object.commodity_type,
        'commodity_sub_type':object.commodity_sub_type,
        'airline_id':str(object.airline_id),
        'operation_type':str(object.operation_type),
        'currency':object.currency,
        'price_type':object.price_type,
        'min_price':object.min_price,
        'service_provider_id':str(object.service_provider_id),
        'cogo_entity_id':str(object.cogo_entity_id),
        'length':object.length,
        'breadth':object.breadth,
        'height': object.height,
        'shipment_type':object.shipment_type,
        'stacking_type':object.stacking_type,
        'rate_type':object.rate_type,
        'source':object.source,
        'maximum_weight':object.maximum_weight,
        'density_category':validity_object['density_category'],
        'density_ratio':"1:{}".format(validity_object['min_density_weight']),
        'initial_volume':validity_object['initial_volume'],
        'initial_gross_weight':validity_object['initial_gross_weight'],
        'available_volume':validity_object['available_volume'],
        'available_gross_weight':validity_object['available_gross_weight'],
        'validity_start': datetime.combine(request.get('validity_start') or  validity_object['validity_start'] ,datetime.min.time()),
        'validity_end':datetime.combine(request.get('validity_end') or validity_object['validity_end'] ,datetime.min.time())
    }
    extend_air_freight_rates_in_delay.apply_async(kwargs={ 'rate': rate,'base_to_base':True }, queue='fcl_freight_rate')


def create_audit(request,object_id):
    update_data={key:value for key,value in request.items() if key not in ['performed_by_id','id','bulk_operation_id']}

    AirFreightRateAudit.create(
        bulk_operation_id=request.get('bulk_operation_id'),
        action_name='update',
        data=jsonable_encoder(update_data),
        object_id=object_id,
        object_type='AirFreightRate',
        performed_by_id=request.get('performed_by_id'),
        validity_id=request.get('validity_id'),
        performed_by_type = request.get("performed_by_type") or "agent"
    )

def validate_validity_object(validity_start, validity_end):
    if not validity_start:
        raise HTTPException(status_code=400, detail="validity_start is invalid")

    if not validity_end:
        raise HTTPException(status_code=400, detail="validity_end is invalid")
    if validity_end > (datetime.now().date() + timedelta(days=60)):
        raise HTTPException(status_code=400, detail="validity_end can not be greater than 60 days from current date")

    if validity_end < (datetime.now().date() +timedelta(days=2)):
        raise HTTPException(status_code=400, detail="validity_end can not be less than 2 days from current date")

    if validity_start < (datetime.now().date() - timedelta(days=15)):
        raise HTTPException(status_code=400, detail="validity_start can not be less than 15 days from current date")

    if validity_end < validity_start:
        raise HTTPException(status_code=400, detail="validity_end can not be lesser than validity_start")
    
    return True

def find_object(request):
    try:
        object=AirFreightRate.select().where(AirFreightRate.id==request.get('id')).first()
    except:
        object=None
    return object

def send_stats(request,freight):
    from services.bramhastra.celery import send_air_rate_stats_in_delay
    send_air_rate_stats_in_delay.apply_async(kwargs = {'action':'update','request':request,'freight':freight},queue = 'statistics')