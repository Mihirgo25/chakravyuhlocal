from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
from services.air_freight_rate.models.air_services_audit import AirServiceAudit
from fastapi import HTTPException
from database.db_session import db


def delete_air_freight_rate_local(request):
    with db.atomic():
        return execute_transaction_code(request)


def execute_transaction_code(request):
    air_freight_rate_local = (
        AirFreightRateLocal.select()
        .where(AirFreightRateLocal.id == request["id"])
        .first()
    )

    if not air_freight_rate_local:
        raise HTTPException(status_code=400, detail="not found")

    air_freight_rate_local.rate_not_available_entry = False

    create_audit(request, air_freight_rate_local.id)

    try:
        air_freight_rate_local.save()

    except:
        raise HTTPException(status_code=500, detail="error in saving")

    return {"id": air_freight_rate_local.id}


def create_audit(request, id):
    AirServiceAudit.create(
        action_name="delete",
        performed_by_id=request.get("performed_by_id"),
        bulk_operation_id=request.get("bulk_operation_id"),
        object_id=id,
        object_type="AirFreightRateLocal",
    )
