
from services.haulage_freight_rate.models.haulage_freight_rate_audit import HaulageFreightRateAudit
from services.haulage_freight_rate.models.haulage_freight_rate_request import HaulageFreightRateRequest
from fastapi import HTTPException
from database.db_session import db
from uuid import UUID


def update_haulage_freight_rate_request(request):
    with db.atomic():
        return execute_transaction_code(request)


def execute_transaction_code(request):
    object = find_object(request)


    if request.get("closing_remarks"):
        if "rate_added" in request.get("closing_remarks"):
            object.reverted_rates_count = (
                object.reverted_rates_count + 1
                if object.reverted_rates_count is not None
                else 1
            )
            reverted_by_user_ids = object.reverted_by_user_ids
            if reverted_by_user_ids is not None:
                reverted_by_user_ids.append(UUID(request.get("performed_by_id")))
            else:
                reverted_by_user_ids = [UUID(request.get("performed_by_id"))]

            object.reverted_by_user_ids = reverted_by_user_ids
            
        object.closing_remarks = (
            object.closing_remarks.append(request.get("closing_remarks"))
            if object.closing_remarks is not None
            else request.get("closing_remarks")
        )

    try:
        object.save()
    except:
        raise HTTPException(
            status_code=500, detail= "Freight rate request updation failed"
        )

    create_audit(request, object.id)

    return {"haulage_freight_rate_request_id": request.get('haulage_freight_rate_request_id')}


def find_object(request):
    object = HaulageFreightRateRequest.select().where(HaulageFreightRateRequest.id == request["haulage_freight_rate_request_id"])
    if object.count()>0:
        return object.first()
    else:
        raise HTTPException(status_code=400, detail=" Haulage Freight rate request id not found")


def create_audit(request, freight_rate_request_id):
    HaulageFreightRateAudit.create(
        action_name="update",
        performed_by_id=request["performed_by_id"],
        data={
            "closing_remarks": request["closing_remarks"],
            "performed_by_id": request["performed_by_id"],
        },
        object_id=freight_rate_request_id,
        object_type="HaulageFreightRateRequest",
        sourced_by_id = request.get('sourced_by_id'),
        procured_by_id = request.get('procured_by_id')
    )
