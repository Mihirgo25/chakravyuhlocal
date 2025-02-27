from fastapi import HTTPException
from database.db_session import db
from services.air_freight_rate.models.air_freight_rate_surcharge import AirFreightRateSurcharge
from services.air_freight_rate.models.air_services_audit import AirServiceAudit


def delete_air_freight_rate_surcharge(request):
    with db.atomic():
        return update_air_freight_rate_surcharge(request)


def update_air_freight_rate_surcharge(request):
    air_freight_rate_surcharge = (
        AirFreightRateSurcharge.select()
        .where(AirFreightRateSurcharge.id == request["id"])
        .first()
    )

    if not air_freight_rate_surcharge:
        raise HTTPException(status_code=404, detail="Surcharge Not Found")

    air_freight_rate_surcharge.rate_not_available_entry = True

    create_audit(request, air_freight_rate_surcharge.id)

    try:
        air_freight_rate_surcharge.save()

    except:
        raise HTTPException(status_code=500, detail="error in saving")

    return {"id": air_freight_rate_surcharge.id}


def create_audit(request, id):
    AirServiceAudit.create(
        action_name="delete",
        performed_by_id=request.get("performed_by_id"),
        bulk_operation_id=request.get("bulk_operation_id"),
        object_id=id,
        object_type="AirFreightRateSurcharge",
    )
