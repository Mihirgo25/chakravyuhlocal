from database.db_session import db
from services.chakravyuh.models.fcl_freight_rate_estimation import FclFreightRateEstimation
from fastapi.exceptions import HTTPException


def create_fcl_freight_rate_estimation(request):
    with db.atomic():
        return create_fcl_estimated_rate(request)


def create_fcl_estimated_rate(request):
    row = {
        "origin_location_id": request.get("origin_location_id"),
        "destination_location_id": request.get("destination_location_id"),
        "container_size": request.get("container_size"),
        "container_type": request.get("container_type"),
        "commodity": request.get("commodity"),
        "currency": request.get("currency"),
        "origin_location_type":request.get("origin_location_type"),
        "destination_location_type":request.get("destination_location_type"),
        "line_items": request.get("line_items")
    }

    rate = (
        FclFreightRateEstimation.select()
        .where(
            FclFreightRateEstimation.origin_location_id
            == request.get("origin_location_id"),
            FclFreightRateEstimation.destination_location_id
            == request.get("destination_location_id"),
            FclFreightRateEstimation.container_size == request.get("container_size"),
            FclFreightRateEstimation.container_type == request.get("container_type"),
            FclFreightRateEstimation.commodity == request.get("commodity")
        )
        .first()
    )

    if not rate:
        rate = FclFreightRateEstimation()
        for key in list(row.keys()):
            setattr(rate, key, row[key])
    else:
        rate.set_line_items(request.get("line_items"))

    try:
        rate.save()
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
    
    rate.create_audit(audit_params(request, rate))
    
    return {
        "id": rate.id
        }

def audit_params(request, rate):
    data = {
        "line_items": request.get("line_items")
    }
    
    param = {
        "source": request.get("source"),
        "object_id": rate.id,
        "action_name": "create",
        "data": data,
        "performed_by_id": request.get('performed_by_id')
    }
    return param
