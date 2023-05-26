from fastapi import HTTPException
from datetime import datetime,timedelta
from peewee import * 
import json
from playhouse.postgres_ext import *
from database.db_session import db
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.models.air_freight_rate_audit import AirFreightRateAudits
def execute(request):
     db.atomic()
     return update_air_freight_rate(request)

def update_air_freight_rate(request):
    object=find_object(request)

    request['weight_slabs'] = sorted(request['weight_slabs'], key=lambda x: x['lower_limit'])
    if not object:
        raise HTTPException(status_code=400,detail="id is invalid")
    validities=json.loads(object['validities'])
    for validity in validities:
        if validity['id']==request['validity_id']:
            if request['validity_start'] and request['validity_end']:
                if validate[request['validity_start'],reqeust['validuty_end']]:
                    validity['validity_start']=request['validity_start']
                    validity['validity_end']=request['validity_end']
                else:
                    raise HTTPException(status_code=400,details="validity start and validity end are invalid")
            validity['status']=True
            if request['min_price'] !=0: object['min_price']=request['min_price']
            object['currency'] = request['currency']
            if request['min_price'] != 0: validity['min_price'] = request['min_price']
            object['weight_slabs'] = request['weight_slabs']
            validity['weight_slabs'] = request['weight_slabs']
            if request['available_volume']: 
                validity['available_volume'] = request['available_volume']
                
            if request['available_gross_weight']: 
                validity['available_gross_weight'] = request['available_gross_weight']
            
            if request['length']:
                object['length'] = request['length'] 
            if request['breadth']:
                object['breadth'] = request['breadth'] 
            if request['height']:
                object['height'] = request['height'] 
            if request['maximum_weight']:
                object['maximum_weight'] = request['maximum_weight'] 
    # updating validities
    AirFreightRate.update(validities = validities).where(AirFreightRate.id == request.get('id'))

    try:
        object.save()
    except Exception as e:
        print("Exception in saving freight rate", e)

    create_audit(request, object.id)
    return {
        id:object.id
    }

def create_audit(request,object_id):
    update_data={}
    update_data['validity_start']=request.get('validity_start')
    update_data['validity_end']=request.get('validity_end')
    update_data['currency']=request.get("currency")
    update_data['min_price']=request.get('min_price')
    update_data['length']=request.get('length')
    update_data['breadth']=request.get('breadth')
    update_data['height']=request.get('height')
    update_data['maximum_weight']=request.get('maximum_weight')
    update_data['available_volume']=request.get('available_volume')
    update_data['available_gross_weight']=request.get('available_gross_weight')
    update_data['weight_slabs']=request.get('weight_slabs')

    AirFreightRateAudits.create(
        bulk_operation_id=request.get('bulk_operation_id'),
        action_name='update',
        data=update_data,
        object_id=object_id,
        object_type='AirFreightRate',
        performed_by_id=request.get('performed_by_id'),
        validity_id=request.get('validity_id')
    )

def validate(validity_start,validity_end):
    if not validity_start:
        return False
    if not validity_end:
        return False
    if validity_end > datetime.now()+timedelta(days=120):
        return False
    if validity_start <datetime.now()-timedelta(days=15):
        return False
    if validity_end <= validity_start:
        return False

def find_object(request):
    try:
        object=AirFreightRate.get_by_id(request['id'])
    except:
        object=None
    return object


        
          
    