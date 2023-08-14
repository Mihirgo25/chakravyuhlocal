from services.fcl_freight_rate.models.fcl_freight_rate_request import (
    FclFreightRateRequest,
)
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from fastapi import HTTPException
from database.db_session import db
from uuid import UUID
from services.fcl_freight_rate.helpers.fcl_freight_statistics_helper import send_request_stats


def update_fcl_freight_rate_request(request):
    with db.atomic():
        return execute_transaction_code(request)


def execute_transaction_code(request):
    object = find_object(request)

    if not object:
        raise HTTPException(status_code=400, detail="Freight rate request id not found")

    if request.get("closing_remarks"):
        if "rate_added" in request.get("closing_remarks"):
            object.reverted_rates_count = (
                object.reverted_rates_count + 1
                if object.reverted_rates_count is not None
                else 1
            )
            object.reverted_by_user_ids = (
                object.reverted_by_user_ids.append(UUID(request.get("performed_by_id")))
                if object.reverted_by_user_ids is not None
                else [UUID(request.get("performed_by_id"))]
            )
        object.closing_remarks = (
            object.closing_remarks.append(request.get("closing_remarks"))
            if object.closing_remarks is not None
            else request.get("closing_remarks")
        )
    if request.get("relevant_supply_agent_ids"):
        object.relevant_supply_agent_ids = (UUID(id) for id in request.get("relevant_supply_agent_ids"))
    try:
        object.save()
    except:
        raise HTTPException(
            status_code=500, detail="Freight rate request updation failed"
        )
                
    send_request_stats('update',request)

    create_audit(request, object.id)


def find_object(request):
    try:
        return (
            FclFreightRateRequest.select()
            .where(FclFreightRateRequest.id == request["fcl_freight_rate_request_id"])
            .first()
        )
    except:
        return None


def create_audit(request, freight_rate_request_id):
    FclFreightRateAudit.create(
        action_name="update",
        performed_by_id=request["performed_by_id"],
        data={
            "closing_remarks": request.get("closing_remarks"),
            "performed_by_id": request.get("performed_by_id"),
        },
        object_id=freight_rate_request_id,
        object_type="FclFreightRateRequest",
    )
