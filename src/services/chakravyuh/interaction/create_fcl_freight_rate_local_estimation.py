from database.db_session import db
from services.chakravyuh.models.fcl_freight_rate_local_estimation import FclFreightRateLocalEstimation


def create_fcl_freight_rate_local_estimation(request):
    with db.atomic():
        return create_fcl_local_estimated_rate(request)


def create_fcl_local_estimated_rate(request):
    row = {
        "location_id": request.get("location_id"),
        "location_type": request.get("location_type"),
        "container_size": request.get("container_size"),
        "container_type": request.get("container_type"),
        "commodity": request.get("commodity"),
        "trade_type": request.get("trade_type"),
        "shipping_line_id":request.get("shipping_line_id"),
        "local_currency":request.get("local_currency")
    }

    rate = (
        FclFreightRateLocalEstimation.select()
        .where(
            FclFreightRateLocalEstimation.location_id == request.get("location_id"),
            FclFreightRateLocalEstimation.container_size == request.get("container_size"),
            FclFreightRateLocalEstimation.container_type == request.get("container_type"),
            FclFreightRateLocalEstimation.shipping_line_id == request.get('shipping_line_id'),
            FclFreightRateLocalEstimation.trade_type == request.get("trade_type"),
        )
        .first()
    )

    if not rate:
        rate = FclFreightRateLocalEstimation()
        for key in list(row.keys()):
            setattr(rate, key, row[key])

    rate.line_items = request.get("line_items")
    rate.status = 'active'

    rate.save()

    return {'id':rate.id}