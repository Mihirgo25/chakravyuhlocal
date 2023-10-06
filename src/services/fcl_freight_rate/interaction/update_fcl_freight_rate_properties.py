from services.fcl_freight_rate.models.fcl_freight_rate_properties import FclFreightRateProperties
# from services.fcl_freight_rate.models.fcl_freight_rate_properties import validate_value_props

from database.db_session import db
from datetime import datetime
from fastapi import HTTPException

def update_fcl_freight_rate_properties(request):
    with db.atomic():
        return execute_transaction_code(request)
    
def execute_transaction_code(request):
    properties_obj = find_properties_obj(request['rate_id'])
    
    if not properties_obj:
        raise HTTPException(status_code=400,detail='Rate Properties id Not Found')
    
    valid_attributes = list(FclFreightRateProperties._meta.fields.keys())
    
    for attr,value in request.items():
        if attr in valid_attributes:
            setattr(properties_obj, attr, value)
        elif attr.startswith("increment"):
            key = attr.replace('increment_', '')
            previous_value = getattr(properties_obj, key)
            setattr(properties_obj,key,previous_value + value )

    properties_obj.validate_value_properties()
    properties_obj.save()

    return {
    'rate_id': request['rate_id']
    }
    
def find_properties_obj(id):
    try:
        updated_properties = FclFreightRateProperties.select().where(FclFreightRateProperties.rate_id==id).first()
        return updated_properties
    except:
        return None