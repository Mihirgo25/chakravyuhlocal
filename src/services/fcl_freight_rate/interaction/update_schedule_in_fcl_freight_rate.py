from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from database.db_session import db
from fastapi import HTTPException
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit


def create_audit(request):
    FclFreightRateAudit.create(
        action_name="update",
        performed_by_id=request.get("performed_by_id"),
        data=request,
        object_type="ScheduleInFreightRate",
    )


def update_schedule_in_fcl_freight_rate(request):
    with db.atomic():
        return execute_transaction_code(request)


def execute_transaction_code(request):
    rate_id = request["rate_id"]
    validity_id = request["validity_id"]
    schedule_id = request["schedule_id"]
    sourced_by_id = request.get("sourced_by_id")
    procured_by_id = request.get("procured_by_id")

    query = FclFreightRate.select().where(FclFreightRate.id == rate_id).first()

    if not query:
        raise HTTPException(
            status=404, detail="No FclFreightRate found with id: {rate_id}"
        )

    validities = query.validities
    new_validities = []
    flag = 0
    for validity_object in validities:
        if validity_object["id"] == validity_id:
            flag = 1
            validity_object["schedule_id"] = schedule_id
            if sourced_by_id is not None:
                query.sourced_by_id = sourced_by_id
            if procured_by_id is not None:
                query.procured_by_id = procured_by_id

        new_validities.append(validity_object)

    if flag:
        query.validities = new_validities
        query.save()

        create_audit(request)
    else:
        raise HTTPException(detail="No Validity found with id: {validity_id}")

    return {"id": rate_id}
