from datetime import datetime
from database.db_session import db 
from fastapi import HTTPException
from services.air_freight_rate.models.air_freight_rate import AirFreightRate

def create_air_freight_rate_feeback(request):
    with db.atomic():
        return execute_transaction_code(request)
    
def execute_transaction_code(request):
    rate=AirFreightRate.select().where(AirFreightRate.id==request.get(['id'])).first()

    if not rate:
        raise HTTPException (status_code=500, detail='id is invalid')
    