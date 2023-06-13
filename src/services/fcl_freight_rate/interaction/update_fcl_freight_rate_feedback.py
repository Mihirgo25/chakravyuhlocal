from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from fastapi import HTTPException
from database.db_session import db


def update_fcl_freight_rate_feedback(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    object = find_object(request)

    if not object:
        raise HTTPException(status_code=400, detail="Freight rate feedback id not found")

    if request.get("feedback_validities"):
        object.feedback_validities = request.get("feedback_validities")

    try:
        object.save()
    except:
        raise HTTPException(
            status_code=500, detail="Freight rate feedback updation failed"
        )

    create_audit(request, object.id)


def find_object(request):
    try:
        return (
            FclFreightRateFeedback.select()
            .where(FclFreightRateFeedback.id == request["fcl_freight_rate_feedback_id"])
            .first()
        )
    except:
        return None


def create_audit(request, freight_rate_feedback_id):
    FclFreightRateAudit.create(
        action_name="update",
        performed_by_id=request["performed_by_id"],
        data={
            "feedback_validities": request.get("feedback_validities")
        },
        object_id=freight_rate_feedback_id,
        object_type="FclFreightRateFeedback",
    )
