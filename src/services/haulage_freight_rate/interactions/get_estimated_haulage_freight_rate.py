from configs.env import DEFAULT_USER_ID
from services.haulage_freight_rate.rate_estimators.haulge_freight_rate_estimator import (
    HaulageFreightRateEstimator,
)

from services.haulage_freight_rate.helpers.haulage_freight_rate_helpers import *


def haulage_rate_calculator(
    origin_location_id,
    destination_location_id,
    commodity,
    containers_count,
    container_type,
    container_size,
    cargo_weight_per_container,
):
    """
    Estimating haulage freight rate
    Response Format:
        {
            "success": True,
            "status_code": 200,
            "list": {
                "base_price": base_price,
                "currency": currency,
                "transit_time": transit_time,
                "line_items": line_items,
            }
        }
    """
    response = {"success": False, "status_code": 200}

    final_data_object = HaulageFreightRateEstimator(
        origin_location_id,
        destination_location_id,
        commodity,
        containers_count,
        container_type,
        cargo_weight_per_container,
        container_size,
    )
    final_data = final_data_object.estimate()
    response["success"] = True
    response["list"] = [final_data]
    return response
