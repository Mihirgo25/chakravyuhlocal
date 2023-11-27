from services.fcl_freight_rate.models.fcl_freight_rate_estimation_ratio import (
    FclFreightRateEstimationRatio,
)


def create_fcl_freight_rate_estimation_ratio(request):
    record = (
        FclFreightRateEstimationRatio.select()
        .where(
            (
                FclFreightRateEstimationRatio.origin_port_id
                == request.get("origin_port_id")
            ),
            (
                FclFreightRateEstimationRatio.destination_port_id
                == request.get("destination_port_id")
            ),
            (FclFreightRateEstimationRatio.commodity == request.get("commodity")),
            (
                FclFreightRateEstimationRatio.container_size
                == request.get("container_size")
            ),
            (
                FclFreightRateEstimationRatio.container_type
                == request.get("container_type")
            ),
            (
                FclFreightRateEstimationRatio.shipping_line_id
                == request.get("shipping_line_id")
            ),
        )
        .first()
    )
    if record:
        record.sl_weighted_ratio = request.get("weighted_ratio")
        record.save()
    else:
        FclFreightRateEstimationRatio.create(
            origin_port_id=request.get("origin_port_id"),
            destination_port_id=request.get("destination_port_id"),
            commodity=request.get("commodity"),
            container_size=request.get("container_size"),
            container_type=request.get("container_type"),
            shipping_line_id=request.get("shipping_line_id"),
            sl_weighted_ratio=request.get("weighted_ratio"),
        )