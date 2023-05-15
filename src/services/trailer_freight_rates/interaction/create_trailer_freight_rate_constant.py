from models.trailer_freight_rate_constant import TrailerFreightRateCharges
from fastapi import HTTPException
from database.db_session import db


def create_trailer_data(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    trailer = TrailerFreightRateCharges.select().where((TrailerFreightRateCharges.id == trailer["id"]) and
                                                       (TrailerFreightRateCharges.country_code == trailer["country_code"]) and
                                                       (TrailerFreightRateCharges.distance == trailer["distance"]) and
                                                       (TrailerFreightRateCharges.insurance == trailer["insurance"]) and
                                                       (TrailerFreightRateCharges.toll == trailer["toll"]) and
                                                       (TrailerFreightRateCharges.driver == trailer["driver"]) and
                                                       (TrailerFreightRateCharges.document == trailer["document"]) and
                                                       (TrailerFreightRateCharges.fuel == trailer["fuel"]) and
                                                       (TrailerFreightRateCharges.handling == trailer["handling"]) and
                                                       (TrailerFreightRateCharges.food == trailer["food"]) and
                                                       (TrailerFreightRateCharges.misc == trailer["misc"]) 
                                                        
                                                     )

    if not trailer:
        trailer=TrailerFreightRateCharges(**request)
    
    if not trailer.save():
        raise HTTPException(status_code=500, detail="Trailer not saved")
    
    # create_audit(request,trailer.id)

    return {'id' : trailer.id}
