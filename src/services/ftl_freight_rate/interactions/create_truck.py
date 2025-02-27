from services.ftl_freight_rate.models.truck import Truck
from fastapi import HTTPException
from database.db_session import db
from services.ftl_freight_rate.models.ftl_services_audit import FtlServiceAudit



def create_audit(request, truck_id):
    data = {
        key: str(value)
        for key, value in request.items()
        if key not in ["performed_by_id"] and not value == None
    }
    FtlServiceAudit.create(
        action_name="create",
        performed_by_id=request["performed_by_id"],
        data=data,
        object_id=truck_id,
        object_type="Truck",
    )


def create_truck_data(request):
    with db.atomic():
        return execute_transaction_code(request)


def execute_transaction_code(request):
    row = {
        "truck_company": request.get("truck_company"),
        "display_name": request.get("display_name"),
        "mileage": request.get("mileage"),
        "mileage_unit": request.get("mileage_unit"),
        "capacity": request.get("capacity"),
        "capacity_unit": request.get("capacity_unit"),
        "vehicle_weight": request.get("vehicle_weight"),
        "vehicle_weight_unit": request.get("vehicle_weight_unit"),
        "fuel_type": request.get("fuel_type"),
        "avg_speed": request.get("avg_speed"),
        "no_of_wheels": request.get("no_of_wheels"),
        "engine_type": request.get("engine_type"),
        "country_id": request.get("country_id"),
        "axels": request.get("axels"),
        "truck_type": request.get("truck_type"),
        "body_type": request.get("body_type"),
        "status": request.get("status") or "active",
        "horse_power": request.get("horse_power"),
        "data": request.get("data"),
    }
    row["truck_name"] = "{}_{}_ton_{}".format(row["truck_company"], row["vehicle_weight"],row["fuel_type"])

    is_truck_present = (
        Truck.select('id')
        .where(
            (Truck.truck_name == row.get("truck_name")),
            (Truck.horse_power == row.get("horse_power")),
            (Truck.country_id == row.get("country_id")),
            (Truck.engine_type == row.get("engine_type")),
            (Truck.capacity == row.get("capacity")),
            (Truck.fuel_type == row.get("fuel_type")),
            (Truck.body_type == row.get("body_type")),
            (Truck.no_of_wheels == row.get("no_of_wheels")),
        )
        .first()
    )

    if not is_truck_present:
        truck = Truck(**row)
        try:
            truck.save()
        except:
            raise HTTPException(status_code=500, detail="truck did not save")

    else:
        raise HTTPException(status_code=500, detail="truck already exist")

    create_audit(request, truck.id)

    return {"id": truck.id}
