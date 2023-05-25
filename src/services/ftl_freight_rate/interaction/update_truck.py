from services.ftl_freight_rate.models.truck import Truck
from fastapi import HTTPException
from database.db_session import db
from datetime import datetime
from services.ftl_freight_rate.models.ftl_services_audit import FtlServiceAudit

def create_audit(request):

    data = {key:str(value) for key, value in request.items() if key not in ['performed_by_id','id'] and not value == None}

    FtlServiceAudit.create(
        action_name = 'update',
        performed_by_id = request['performed_by_id'],
        data = data,
        object_id = request['id'],
        object_type = 'Truck'
    )

def update_truck_data(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    if type(request) != dict:
        request = request.dict(exclude_none = False)

    update_params = {key: value for key, value in request.items() if key in ['mileage', 'mileage_unit', 'capacity', 'capacity_unit', 'vehicle_weight', 'vehicle_weight_unit', 'fuel_type', 'avg_speed', 'no_of_wheels', 'engine_type', 'axels', 'truck_type', 'body_type', 'status', 'horse_power','data']}
    update_params['updated_at'] = datetime.now()
    truck = Truck.update(update_params).where(Truck.id == request['id'])

    if truck.execute() == 0:
        raise HTTPException(status_code=500, detail="Truck not updated")
    create_audit(request)

    return {'id' : request['id']}
