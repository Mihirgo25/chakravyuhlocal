from services.ftl_freight_rate.models.ftl_freight_rate_rule_set import FtlFreightRateRuleSet
from fastapi import HTTPException
from database.db_session import db
from datetime import datetime
from services.ftl_freight_rate.models.ftl_services_audit import FtlServiceAudit


def create_audit(request):
    data = {
        key: str(value)
        for key, value in request.items()
        if key not in ["performed_by_id", "id"] and not value == None
    }

    FtlServiceAudit.create(
        action_name="update",
        performed_by_id=request["performed_by_id"],
        data=data,
        object_id=request["id"],
        object_type="FtlFreightRateRuleSet",
    )


def update_ftl_rule_set_data(request):
    with db.atomic():
        return execute_transaction_code(request)


def execute_transaction_code(request):
    if type(request) != dict:
        request = request.dict(exclude_none=False)

    update_params = {
        key: value
        for key, value in request.items()
        if key
        in [
            "location_type",
            "truck_type",
            "process_type",
            "process_unit",
            "process_value",
            "process_currency",
            "status",
        ]
    }
    update_params["updated_at"] = datetime.now()
    ftl_rule_set = FtlFreightRateRuleSet.update(update_params).where(
        FtlFreightRateRuleSet.id == request["id"]
    )

    if ftl_rule_set.execute() == 0:
        raise HTTPException(status_code=500, detail="ftl rule set not updated")
    create_audit(request)

    return {"id": request["id"]}
