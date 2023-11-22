from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from database.db_session import db
from fastapi import HTTPException
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit


def create_audit(request):
    request_data = {
        "rate_id": request["rate_id"],
        "validity_id": request["validity_id"],
        "schedule_id": request["schedule_id"],
    }
    FclFreightRateAudit.create(
        action_name="update",
        performed_by_id=request.get("performed_by_id"),
        data=request_data,
        object_type="ScheduleInFreightRate",
    )


def update_schedule_in_fcl_freight_rate(request):
    with db.atomic():
        return execute_transaction_code(request)


def execute_transaction_code(request):
    rate_id = request["rate_id"]
    validity_id = request["validity_id"]
    schedule_id = request["schedule_id"]
    sourced_by_id = request.get("performed_by_id")

    freight = FclFreightRate.select().where(FclFreightRate.id == rate_id).first()

    if not freight:
        raise HTTPException(
            status=404, detail="No freight found with id: {rate_id}"
        )

    validities = freight.validities
    new_validities = []
    validity_found = False
    for validity_object in validities:
        if validity_object["id"] == validity_id:
            validity_found = True
            validity_object["schedule_id"] = schedule_id
               
        new_validities.append(validity_object)

    if validity_found:
        freight.validities = new_validities
        freight.sourced_by_id = sourced_by_id
        freight.save()

        create_audit(request)
    else:
        raise HTTPException(detail="No Validity found with id: {validity_id}")

    return {"id": rate_id}
