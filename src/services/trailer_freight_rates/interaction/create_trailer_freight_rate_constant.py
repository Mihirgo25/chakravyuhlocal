from services.trailer_freight_rates.models.trailer_freight_rate_constant import TrailerFreightRateCharges
from fastapi import HTTPException
from database.db_session import db
from playhouse.shortcuts import model_to_dict

def create_trailer_constant_data(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    data = TrailerFreightRateCharges.select().where(
                (TrailerFreightRateCharges.country_code == request["country_code"]),
                (TrailerFreightRateCharges.currency_code == request["currency_code"]),
                (TrailerFreightRateCharges.status == 'active')).first()

    if data:
        # for k, v in request.items():
        #     setattr(data, k, v)
        # data.save()
        return {'id' : data.id}
    
    data=TrailerFreightRateCharges.create(**request)
    
    if not data.save():
        raise HTTPException(status_code=500, detail="Data not saved")
    
    return {'id' : data.id}