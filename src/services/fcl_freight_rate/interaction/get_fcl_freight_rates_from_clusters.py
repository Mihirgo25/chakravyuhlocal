from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_location_cluster import (
    FclFreightLocationCluster,
)
from services.fcl_freight_rate.models.fcl_freight_location_cluster_mapping import (
    FclFreightLocationClusterMapping,
)
from fastapi.encoders import jsonable_encoder
import random
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


USD_CURRENCY = "USD"


def get_shipping_line_mapping(critical_freight_rates):
    """Generate a mapping of shipping line IDs to their average prices.

    Args:
        critical_freight_rates

    Returns:
        dict: Mapping of shipping line IDs to their average prices.
    """
    shipping_line_data = {}
    shipping_line_mapping = {}

    for rate in critical_freight_rates:
        validities = rate["validities"]
        total_price = 0.0
        count = 0
        shipping_line_id = rate["shipping_line_id"]

        for validity in validities:
            line_items = validity.get("line_items", [])
            for line_item in line_items:
                if line_item["code"] == "BAS":
                    price = line_item.get("price", 0.0)
                    if line_item["currency"] != USD_CURRENCY:
                        price = common.get_money_exchange_for_fcl(
                            dict(
                                from_currency=line_item["currency"],
                                to_currency=USD_CURRENCY,
                                price=price,
                            )
                        ).get("price", 0.0)
                    total_price += float(price)
                    count += 1

        if count > 0:
            if shipping_line_id in shipping_line_data:
                shipping_line_data[shipping_line_id]["total_price"] += total_price
                shipping_line_data[shipping_line_id]["count"] += count
            else:
                shipping_line_data[shipping_line_id] = {
                    "total_price": total_price,
                    "count": count,
                }

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


def get_create_params(
    origin_port_id,
    destination_port_id,
    request,
    ff_mlo,
    shipping_line_ids,
    get_default_create_params,
):
    """Generate parameters for creating freight rate entries based on various criteria.

    Args:
        origin_port_id,
        destination_port_id,
        request,
        ff_mlo,
        shipping_line_ids

    Returns:
        list: List of parameters for creating freight rate entries.
    """
    is_origin_base_port = (
        FclFreightLocationCluster.select()
        .where(FclFreightLocationCluster.base_port_id == origin_port_id)
        .exists()
    )
    is_destination_base_port = (
        FclFreightLocationCluster.select()
        .where(FclFreightLocationCluster.base_port_id == destination_port_id)
        .exists()
    )

    origin_base_port_id = None
    destination_base_port_id = None
    if is_origin_base_port:
        origin_base_port_id = origin_port_id
    else:
        origin_cluster_location_object = (
            FclFreightLocationCluster.select(FclFreightLocationCluster.base_port_id)
            .join(FclFreightLocationClusterMapping)
            .where(FclFreightLocationClusterMapping.location_id == origin_port_id)
            .first()
        )
        origin_base_port_id = str(origin_cluster_location_object.base_port_id)

    if is_destination_base_port:
        destination_base_port_id = destination_port_id
    else:
        destination_cluster_location_object = (
            FclFreightLocationCluster.select(FclFreightLocationCluster.base_port_id)
            .join(FclFreightLocationClusterMapping)
            .where(FclFreightLocationClusterMapping.location_id == destination_port_id)
            .first()
        )
        destination_base_port_id = str(destination_cluster_location_object.base_port_id)

    critical_freight_rates_query = FclFreightRate.select(
        FclFreightRate.id,
        FclFreightRate.shipping_line_id,
        FclFreightRate.validities,
        FclFreightRate.weight_limit,
    ).where(
        FclFreightRate.origin_port_id == origin_base_port_id,
        FclFreightRate.destination_port_id == destination_base_port_id,
        FclFreightRate.container_size == request["container_size"],
        FclFreightRate.container_type == request["container_type"],
        FclFreightRate.commodity == request["commodity"],
        FclFreightRate.service_provider_id.in_(ff_mlo),
        ~FclFreightRate.rate_not_available_entry,
        FclFreightRate.rate_type == "market_place",
        FclFreightRate.last_rate_available_date >= request["validity_start"],
    )

    critical_freight_rates = jsonable_encoder(
        list(critical_freight_rates_query.dicts())
    )
    create_params = []

    if not critical_freight_rates:
        return create_params

    if get_default_create_params:
        return default_create_params(
            request,
            origin_port_id,
            destination_port_id,
            critical_freight_rates,
            create_params,
            shipping_line_ids
        )

    shipping_line_mapping = {}
    shipping_line_mapping = get_shipping_line_mapping(critical_freight_rates)
    normalized_median = get_current_median(
        request,
        origin_port_id,
        destination_port_id,
        destination_base_port_id,
        origin_base_port_id,
        shipping_line_mapping,
        shipping_line_ids,
    )
    
    secondary_factor = 1.2 if not is_origin_base_port else 1
    if not is_destination_base_port:
        secondary_factor *= 1.2

    for shipping_line_id in shipping_line_ids:
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
            "shipping_line_id": shipping_line_id,
            "weight_limit": critical_freight_rates[0]["weight_limit"],
            "service_provider_id": DEFAULT_SERVICE_PROVIDER_ID,
            "performed_by_id": DEFAULT_USER_ID,
            "procured_by_id": DEFAULT_USER_ID,
            "sourced_by_id": DEFAULT_USER_ID,
            "source": "rate_extension",
            "mode": "rate_manufactured",
        }

        if origin_port_id != request["origin_port_id"]:
            param["origin_main_port_id"] = origin_port_id

        if destination_port_id != request["destination_port_id"]:
            param["destination_main_port_id"] = destination_port_id
            
        randomization_factor = random.uniform(1, 1.13)
        for validity in critical_freight_rates[0]["validities"]:
            param["validity_start"] = datetime.strptime(
                datetime.now().date().isoformat(), "%Y-%m-%d"
            )
            param["validity_end"] = datetime.strptime(
                (datetime.now() + timedelta(days=3)).date().isoformat(), "%Y-%m-%d"
            )
            param["schedule_type"] = validity["schedule_type"]
            param["payment_term"] = validity["payment_term"]
            line_items = validity["line_items"]
            line_items = jsonable_encoder(line_items)
            for line_item in line_items:
                if line_item["code"] == "BAS":
                    sl_ratio = shipping_line_mapping.get(shipping_line_id, {}).get(
                        "sl_ratio", 1
                    )
                    line_item["price"] = round(normalized_median * sl_ratio * secondary_factor, 2)
                    if sl_ratio == 1:
                        line_item["price"]= round(line_item["price"] * randomization_factor, 2)
            param["line_items"] = line_items

        create_params.append(param)

    return create_params


def default_create_params(
    request, origin_port_id, destination_port_id, critical_freight_rates, create_params, shipping_line_ids
):
    serviceable_rates = [rate for rate in critical_freight_rates if  rate["shipping_line_id"] in shipping_line_ids]
   
    for rate in serviceable_rates:
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
