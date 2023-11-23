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
    schedule_id = request.get("schedule_id")
    sourced_by_id = request["performed_by_id"]
    schedule_type = request["schedule_type"]
    
    deleted=True
    if schedule_id:
        deleted=False
        
    freight = FclFreightRate.select().where(FclFreightRate.id == rate_id).first()

    if not freight:
        raise HTTPException(status=404, detail=f"No freight found with id: {rate_id}")

    validities = freight.validities

    validity_object_found = None

    for validity_object in validities:
        if validity_object["id"] == validity_id:
            validity_object_found = validity_object
            break
            

    if validity_object_found:
        validity_start=validity_object['validity_start']
        validity_end=validity_object['validity_end']
        line_items=validity_object['line_items']
        schedule_type=schedule_type
        payment_term=validity_object['payment_term']
        freight.set_validities(validity_start,validity_end,line_items,schedule_type,deleted,payment_term,{},None,schedule_id)
        freight.sourced_by_id = sourced_by_id
        freight.save()

        create_audit(request)
    else:
        raise HTTPException(status=404, detail=f"No Validity found with id: {validity_id}")

    return {"id": rate_id}
