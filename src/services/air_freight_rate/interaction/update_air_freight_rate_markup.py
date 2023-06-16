from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from fastapi import FastAPI, HTTPException
from services.air_freight_rate.models.air_freight_rate_audit import AirFreightRateAudit
from database.db_session import db


def create_audit(request):
    audit_data = {
        "validity_id": request.get("validity_id"),
        "validity_start": str(request.get("validity_start")),
        "validity_end": str(request.get("validity_end")),
    }
    AirFreightRateAudit.create(
        action_name="edit",
        performed_by_id=request.get("performed_by_id"),
        bulk_operation_id=request.get("bulk_operation_id"),
        data=audit_data,
        validity_id=request.get("validity_id"),
    )


def update_air_freight_rate_markup(request):
    with db.atomic():
        return execute_transaction_code(request)


def execute_transaction_code(request):
    object = AirFreightRate.select().where(AirFreightRate.id == request["id"]).first()
    if not object:
        raise HTTPException(status_code=400, detail=" Rate not found")

    for t in object.validities:
        if t.get("id") == request.get("validity_id"):
            print("asdfghjkl",type(t['validity_start']))
            t["validity_start"] = str(request.get("validity_start").date())
            t["validity_end"] = str(request.get("validity_end").date())
            object.set_validities(
                request.get("validity_start").date(),
                request.get("validity_end").date(),
                t.get("min_price"),
                None,
                t.get("weight_slabs"),
                True,
                request.get("validity_id"),
                t.get("density_category"),
                None,
                None,
                None,
                None,
                None,
                object.rate_type,
            )
            object.set_last_rate_available_date

    try:
        object.save()
    except Exception:
        raise HTTPException(status_code=500, detail="MarkUp not updated")

    create_audit(request)

    return {"id": str(object.id)}