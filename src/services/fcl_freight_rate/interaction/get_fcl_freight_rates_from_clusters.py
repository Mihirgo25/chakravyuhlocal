from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_location_cluster import (
    FclFreightLocationCluster,
)
from services.fcl_freight_rate.models.fcl_freight_location_cluster_mapping import (
    FclFreightLocationClusterMapping,
)
from fastapi.encoders import jsonable_encoder
from datetime import datetime, timedelta
import concurrent.futures
from configs.fcl_freight_rate_constants import DEFAULT_SERVICE_PROVIDER_ID
from configs.env import DEFAULT_USER_ID
from services.fcl_freight_rate.interaction.create_fcl_freight_rate import (
    create_fcl_freight_rate_data,
)
from database.rails_db import get_ff_mlo
from services.fcl_freight_rate.models.fcl_freight_rate_estimation_ratio import (
    FclFreightRateEstimationRatio,
)
from configs.global_constants import CHINA_COUNTRY_ID, INDIA_COUNTRY_ID
from micro_services.client import common


def get_shipping_line_mapping(critical_freight_rates):
    """Generate a mapping of shipping line IDs to their average prices.

    Args:
        critical_freight_rates

    Returns:
        dict: Mapping of shipping line IDs to their average prices.
    """
    shipping_line_mapping = {}
    shipping_line_data = {}

    for rate in critical_freight_rates:
        validities = rate["validities"]
        total_price = 0.0
        count = 0
        for validity in validities:
            line_items = validity.get("line_items", [])
            for line_item in line_items:
                if line_item["code"] == "BAS":
                    price = line_item.get("price", 0.0)
                    if line_item["currency"] != "USD":
                        price = common.get_money_exchange_for_fcl(
                            dict(
                                from_currency=line_item["currency"],
                                to_currency="USD",
                                price=price,
                            )
                        ).get("price", 0.0)
                    total_price += float(price)
                    count += 1

        if count > 0:
            shipping_line_id = rate["shipping_line_id"]

            if shipping_line_id in shipping_line_data:
                shipping_line_data[shipping_line_id]["total_price"] += total_price
                shipping_line_data[shipping_line_id]["count"] += count
            else:
                shipping_line_data[shipping_line_id] = {
                    "total_price": total_price,
                    "count": count,
                }

    shipping_line_mapping = {}
    for shipping_line_id, data in shipping_line_data.items():
        total_price = data["total_price"]
        count = data["count"]
        avg_price = float(total_price / count)
        shipping_line_mapping[shipping_line_id] = {"sl_avg": avg_price}

    return shipping_line_mapping


def get_current_median(
    request,
    origin_port_id,
    destination_port_id,
    destination_base_port_id,
    origin_base_port_id,
    shipping_line_mapping,
    shipping_line_ids,
):
    """Calculate the normalized median for shipping line ratios based on given parameters.

    Args:
        request,
        origin_port_id,
        destination_port_id,
        destination_base_port_id,
        origin_base_port_id,
        shipping_line_mapping,
        shipping_line_ids

    Returns:
        float: The normalized median value.
    """
    data = {
        "origin_port_id": request["origin_port_id"],
        "destination_port_id": request["destination_port_id"],
    }

    if origin_port_id != request["origin_port_id"]:
        data["origin_main_port_id"] = origin_port_id

    if destination_port_id != request["destination_port_id"]:
        data["destination_main_port_id"] = destination_port_id

    unique_shipping_line_ids = list(
        set(shipping_line_ids + list(shipping_line_mapping.keys()))
    )

    query = FclFreightRateEstimationRatio.select().where(
        FclFreightRateEstimationRatio.commodity == request["commodity"],
        FclFreightRateEstimationRatio.container_type == request["container_type"],
        FclFreightRateEstimationRatio.container_size == request["container_size"],
        FclFreightRateEstimationRatio.destination_port_id == destination_base_port_id,
        FclFreightRateEstimationRatio.origin_port_id == origin_base_port_id,
        FclFreightRateEstimationRatio.shipping_line_id << unique_shipping_line_ids,
    )

    sl_ratio_mapping = {}

    for row in query:
        key = str(row.shipping_line_id)
        sl_ratio_mapping[key] = row.sl_weighted_ratio

    sum = 0.0
    count = 0
    normalized_median = 0

    for shipping_line_id in unique_shipping_line_ids:
        sl_ratio_value = sl_ratio_mapping.get(shipping_line_id, 1)
        sl_avg_value = shipping_line_mapping.get(shipping_line_id, {}).get("sl_avg")

        shipping_line_info = shipping_line_mapping.get(
            shipping_line_id, {"sl_avg": None}
        )
        shipping_line_info["sl_ratio"] = sl_ratio_value
        shipping_line_mapping[shipping_line_id] = shipping_line_info

        if sl_avg_value is not None:
            sum += float(sl_avg_value / sl_ratio_value)
            count += 1

    if count > 0:
        normalized_median = sum / count

    return normalized_median


def get_fcl_freight_rates_from_clusters(request, serviceable_shipping_lines):
    ff_mlo = get_ff_mlo()

    create_params = []
    get_default_create_params = (
        request["origin_country_id"] != CHINA_COUNTRY_ID
        or request["destination_country_id"] != INDIA_COUNTRY_ID
    )

    for hash in serviceable_shipping_lines:
        origin_port_id = hash.get("origin_main_port_id") or hash.get("origin_port_id")
        destination_port_id = hash.get("destination_main_port_id") or hash.get(
            "destination_port_id"
        )
        shipping_line_ids = hash.get("shipping_lines")
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(
                    get_create_params,
                    origin_port_id,
                    destination_port_id,
                    request,
                    ff_mlo,
                    shipping_line_ids,
                    get_default_create_params,
                )
            ]
        create_params.extend(futures)

    for i in range(len(create_params)):
        create_params[i] = create_params[i].result()

    create_params = [sublist for list in create_params for sublist in list if sublist]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(create_fcl_freight_rate_data, param)
            for param in create_params
        ]



def default_create_params(
    request, origin_port_id, destination_port_id, critical_freight_rates, create_params
):
    for rate in critical_freight_rates:
        param = {
            "origin_port_id": request["origin_port_id"],
            "destination_port_id": request["destination_port_id"],
            "origin_country_id": request["origin_country_id"],
            "destination_country_id": request["destination_country_id"],
            "container_size": request["container_size"],
            "container_type": request["container_type"],
            "commodity": request["commodity"]
            if request.get("commodity")
            else "general",
            "shipping_line_id": rate["shipping_line_id"],
            "weight_limit": rate["weight_limit"],
            "service_provider_id": DEFAULT_SERVICE_PROVIDER_ID,
            "performed_by_id": DEFAULT_USER_ID,
            "procured_by_id": DEFAULT_USER_ID,
            "sourced_by_id": DEFAULT_USER_ID,
            "source": "rate_extension",
            "mode": "cluster_extension",
            "accuracy": 80,
            "extended_from_object_id": rate["id"],
        }

        if origin_port_id != request["origin_port_id"]:
            param["origin_main_port_id"] = origin_port_id

        if destination_port_id != request["destination_port_id"]:
            param["destination_main_port_id"] = destination_port_id

        for validity in rate["validities"]:
            param["validity_start"] = datetime.strptime(
                datetime.now().date().isoformat(), "%Y-%m-%d"
            )
            param["validity_end"] = datetime.strptime(
                (datetime.now() + timedelta(days=3)).date().isoformat(), "%Y-%m-%d"
            )
            param["schedule_type"] = validity["schedule_type"]
            param["payment_term"] = validity["payment_term"]
            param["line_items"] = validity["line_items"]
            create_params.append(param)

    return create_params
