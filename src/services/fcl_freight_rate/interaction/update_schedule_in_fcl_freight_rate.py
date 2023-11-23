from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from database.db_session import db
from fastapi import HTTPException
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit


def create_audit(request):
    data = {
        "validity_id": request["validity_id"],
        "schedule_id": request["schedule_id"],
    }
    FclFreightRateAudit.create(
        action_name="schedule_update",
        performed_by_id=request["performed_by_id"],
        data=data,
        object_id={request["rate_id"]},
        object_type="FclFreightRate",
    )


def update_schedule_in_fcl_freight_rate(request):
    with db.atomic():
        return execute_transaction_code(request)


def execute_transaction_code(request):
    rate_id = request["rate_id"]
    validity_id = request["validity_id"]
    schedule_id = request["schedule_id"]
    sourced_by_id = request["performed_by_id"]
    schedule_type = request["schedule_type"]

    freight = FclFreightRate.select().where(FclFreightRate.id == rate_id).first()

    if not freight:
        raise HTTPException(status=404, detail=f"No freight found with id: {rate_id}")

    validities = freight.validities
    new_validities = []
    validity_found = False
    for validity_object in validities:
        if validity_object["id"] == validity_id:
            validity_found = True
            validity_object["schedule_id"] = schedule_id
            validity_object["schedule_type"] = schedule_type

        new_validities.append(validity_object)

    if validity_found:
        freight.validities = new_validities
        freight.sourced_by_id = sourced_by_id
        freight.save()

        create_audit(request)
    else:
        raise HTTPException(status=404, detail=f"No Validity found with id: {validity_id}")

    return {"id": rate_id}
