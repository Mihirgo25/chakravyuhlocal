from services.ftl_freight_rate.models.truck import Truck
from fastapi import HTTPException
from database.db_session import db
from services.ftl_freight_rate.models.ftl_services_audit import FtlServiceAudit
import pandas as pd

def create_audit(request, truck_id):
    data = {key:str(value) for key, value in request.items() if key not in ['performed_by_id'] and not value == None}
    FtlServiceAudit.create(
        action_name = 'create',
        performed_by_id = request['performed_by_id'],
        data = data,
        object_id = truck_id,
        object_type = 'Truck'
    )

def create_truck_data(request):
    with db.atomic():
        return execute_transaction_code(request)

        
    
def execute_transaction_code(request):
    
    truck = Truck.select().where((Truck.truck_name == request['name']) and 
                                 (Truck.horse_power == request['horse_power']) and
                                 (Truck.country_id == request['country_id']) and
                                 (Truck.engine_type == request['engine_type']) and
                                 (Truck.fuel_type == request['fuel_type']) and
                                 (Truck.no_of_wheels == request['no_of_tyres'])).first()

    if not truck:
       truck = Truck(**request)

    if not truck.save():
        raise HTTPException(status_code=500, detail="Truck not saved")
    
    create_audit(request,truck.id)

    return {'id' : truck.id}

