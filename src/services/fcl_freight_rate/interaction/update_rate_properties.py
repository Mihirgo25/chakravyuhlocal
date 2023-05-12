from services.fcl_freight_rate.models.fcl_freight_rate_properties import RateProperties
# from services.fcl_freight_rate.models.fcl_freight_rate_properties import validate_value_props

from database.db_session import db
from datetime import datetime
from fastapi import HTTPException

def update_rate_props(request):
    object_type = 'Fcl_Rate_Properties'
    with db.atomic():
        return execute_transaction_code(request)
def execute_transaction_code(request):
    updated_properties = RateProperties.get(**{'rate_id' : request['rate_id']})
    if not updated_properties:
        raise HTTPException(status_code=400,detail='Rate Properties id Not Found')
    request['updated_at'] = datetime.now()
    for attr,value in request.items():
        setattr(updated_properties, attr, value)
    updated_properties.validate_value_props()
    if not updated_properties.save():
        raise HTTPException(status_code=500, detail="Rate Properties not saved")
    return {
    'rate_id': request['rate_id']
    }


    