from fastapi import HTTPException
from datetime import * 
from peewee import * 
import json
from playhouse.postgres_ext import *
from database.db_session import db
from fastapi.encoders import jsonable_encoder
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.models.air_freight_rate_audit import AirFreightRateAudit

def update_air_freight_rate(request):
      with db.atomic():
        return execute(request)

def execute(request):
    object=find_object(request)

    if not object:
        raise HTTPException(status_code=400,detail="id is invalid")
    
    validities=object.validities

    for validity in validities:
        if validity['id']==request.get('validity_id'):

            if request.get('validity_start') and request.get('validity_end'):

                if validate_validity_object(request['validity_start'],request['validity_end']):

                    validity['validity_start']=datetime.strftime(request.get('validity_start'),'%Y-%m-%d')
                    validity['validity_end']=datetime.strftime(request.get('validity_end'),'%Y-%m-%d')
            
            validity['status']=True

            if request.get('min_price') !=0.0: 

                object.min_price=request['min_price']
                validity['min_price'] = request['min_price']

            if request.get('currency'):

                object.currency = request['currency']

            if request.get('weight_slabs'):
                object.weight_slabs = sorted(request.get('weight_slabs'), key=lambda x: x['lower_limit'])
                validity['weight_slabs'] = sorted(request.get('weight_slabs'), key=lambda x: x['lower_limit'])

            if request.get('available_volume'): 
                validity['available_volume'] = request['available_volume']
                
            if request.get('available_gross_weight'): 
                validity['available_gross_weight'] = request['available_gross_weight']
            
            if request.get('length'):
                object.length = request.get('length') 

            if request.get('breadth'):
                object.breadth = request.get('breadth') 

            if request.get('height'):
                object.height = request.get('height')

            if request.get('maximum_weight'):
                object.maximum_weight = request.get('maximum_weight')

            object.validities=validities

            break

    try:
        object.save()
    except Exception as e:
        print("Exception in saving freight rate", e)

    create_audit(request, object.id)
    return {
        'id':object.id
    }

def create_audit(request,object_id):
    update_data={key:value for key,value in request.items() if key not in ['performed_by_id','id','bulk_operation_id','procured_by_id','sourced_by_id']}

    AirFreightRateAudit.create(
        bulk_operation_id=request.get('bulk_operation_id'),
        action_name='update',
        data=jsonable_encoder(update_data),
        object_id=object_id,
        object_type='AirFreightRate',
        performed_by_id=request.get('performed_by_id'),
        validity_id=request.get('validity_id')
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


        
          
    