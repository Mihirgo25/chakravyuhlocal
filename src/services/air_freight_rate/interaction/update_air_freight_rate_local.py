from database.db_session import db 
from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
from fastapi import HTTPException
from datetime import *
from services.air_freight_rate.models.air_freight_rate_audit import AirFreightRateAudits
# import sel


def execute(request):
    with db.atomic():
        return update_air_freight_rate_local(request)
    


def update_air_freight_rate_local(request):
    object=find_object(request)

    if not object:
        raise HTTPException(status_code=400,detail='id is invalid')
    

    if request.get('line_items'):
        object.line_items=request.get('line_items')
        object.update_line_item_messages()
        
    try:
        object.save()
    except Exception as e:
        print(e)
    create_audit(request,object.id)
    return{
        'id':object.id
    }

    
def create_audit(request,object_id):
    update_data={}
    update_data['line_items']=request.get("line_items")
    update_data['code']=request.get("code")
    update_data['unit']=request.get("unit")
    update_data['min_price']=request.get("min_price")
    update_data['currency']=request.get("currency")
    update_data['remarks']=request.get("remarks")
    update_data['slabs']=request.get("slabs")
    update_data['lower_limit']=request.get("lower_limit")
    update_data['upper_limit']=request.get("upper_limit")
    update_data['price']=request.get("price")

    AirFreightRateAudits.create(
        bulk_operation_id=request.get('bulk_operation_id'),
        action_name='update',
        data=update_data,
        object_id=object_id,
        object_type='AirFreightRateLocal',
        performed_by_id=request.get('performed_by_id'),
        validity_id=request.get('validity_id')
    )




def find_object(request):
    try:
        object=AirFreightRateLocal.select().where(AirFreightRateLocal.id==request.get('id')).first()
    except:
        object=None
    return object
