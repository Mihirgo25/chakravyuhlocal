from services.haulage_freight_rate.models.haulage_freight_rate_feedback import (
    HaulageFreightRateFeedback,
)
from services.haulage_freight_rate.models.haulage_freight_rate_audit import (
    HaulageFreightRateAudit,
)
from fastapi import HTTPException
from database.db_session import db


def delete_haulage_freight_rate_feedback(request):
    with db.atomic():
        return execute_transaction_code(request)


def execute_transaction_code(request):
    """
    Delete Haulage Freight Rate Feedbacks
    Response Format:
        {"ids": deleted_haulage_freight_rate_ids}
    """

    from celery_worker import (
        update_multiple_service_objects,
    )

    objects = find_objects(request)

    for obj in objects:
        obj.status = "inactive"

        if request.get('reverted_rate_id') and request.get('reverted_rate'):
            obj.reverted_rate_id=request.get('reverted_rate_id')
            obj.reverted_rate = request.get('reverted_rate')
        
        obj.closed_by_id = request["performed_by_id"]

        obj.closing_remarks = request.get("closing_remarks")

        try:
            obj.save()
        except:
            raise HTTPException(
                status_code=400, detail="Freight rate local deletion failed"
            )

        create_audit(request, obj.id)
        update_multiple_service_objects.apply_async(kwargs={"object": obj}, queue="low")

    return {"ids": request["haulage_freight_rate_feedback_ids"]}


def find_objects(request):
    object = HaulageFreightRateFeedback.select().where(
        HaulageFreightRateFeedback.id << request["haulage_freight_rate_feedback_ids"],
        HaulageFreightRateFeedback.status == "active",
    )
    if object.count() > 0:
        return object
    else:
        raise HTTPException(
            status_code=404, detail="Freight rate feedback id not found"
        )


def create_audit(request, freight_rate_feedback_id):
    HaulageFreightRateAudit.create(
        action_name="delete",
        performed_by_id=request["performed_by_id"],
        data={
            "closing_remarks": request["closing_remarks"],
            "performed_by_id": request["performed_by_id"],
        },
        object_id=freight_rate_feedback_id,
        object_type="HaulageFreightRateFeedback",
        sourced_by_id = request.get('sourced_by_id'),
        procured_by_id = request.get('procured_by_id')
    )
