from fastapi import HTTPException
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from playhouse.postgres_ext import *
from datetime import *
from services.air_freight_rate.constants.air_freight_rate_constants import (
    AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO,
)
from services.air_freight_rate.constants.air_freight_rate_constants import AIR_TRADE_IMPORT_TYPE
from services.air_freight_rate.constants.air_freight_rate_constants import AIR_IMPORTS_HIGH_DENSITY_RATIO
from services.air_freight_rate.constants.air_freight_rate_constants import AIR_IMPORTS_LOW_DENSITY_RATIO
from services.air_freight_rate.constants.air_freight_rate_constants import AIR_EXPORTS_HIGH_DENSITY_RATIO
from services.air_freight_rate.constants.air_freight_rate_constants import AIR_EXPORTS_LOW_DENSITY_RATIO
from services.air_freight_rate.constants.air_freight_rate_constants import MAX_CARGO_LIMIT
from configs.definitions import AIR_FREIGHT_CHARGES


def get_air_freight_rate(request):
    if not all_fields_present(request):
        return {}
    object = find_object(request)
    if not object:
        return {}

    if (
        request.get("weight")
        and request.get("volume")
        and request.get("cargo_readiness_date")
    ):
        required_weight = get_chargable_weight(request)
        validities = object.validities
        for validity in validities:
            freight_object = build_freight_object(validity, required_weight, request)

            if not freight_object:
                continue
    return {"freight_rate": freight_object}


def build_freight_object(freight_validity, required_weight, request):
    validity_start = datetime.strptime(
        freight_validity["validity_start"], "%Y-%m-%dT%H:%M:%S.%fz"
    ).date()
    validity_end = datetime.strptime(
        freight_validity["validity_end"], "%Y-%m-%dT%H:%M:%S.%fz"
    ).date()

    if (
        validity_start > request.get("validity_end").date()
        or validity_end <= request.get("validity_start").date()
        or request.get("cargo_readiness_date").date() < validity_start
        or request.get("cargo_readiness_date").date() > validity_end
    ):
        return None

    freight_object = get_freight_object(freight_validity, request)
    required_slab = get_required_weight_slab(freight_validity, required_weight, request)
    if not required_slab:
        return None

    freight_object["required_slab"] = required_slab
    price = required_slab["tariff_price"]
    min_price = freight_validity["min_price"]
    currency = freight_validity["currency"]
    line_item = {
        "code": "BAS",
        "unit": "per_kg",
        "price": price,
        "currency": currency,
        "min_price": min_price,
        "remarks": [],
    }
    code_config = AIR_FREIGHT_CHARGES[line_item["code"]]
    line_item["quantity"] = required_weight
    total_price = line_item["quantity"] * line_item["price"]
    if line_item["min_price"] > total_price:
        line_item["total_price"] = line_item["min_price"]
    line_item["total_price"] = total_price
    line_item["name"] = code_config["name"]
    line_item["source"] = "system"
    freight_object["line_items"].append(line_item)
    density_params = get_density_params(freight_object, required_weight, request)
    lala = get_density_wise_rate(density_params)
    print(lala)

    return lala


def get_chargable_weight(request):
    volumetric_weight = (
        request.get("volume") * AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO
    )
    chargeable_weight = max(volumetric_weight, request.get("weight"),request.get('chargeable_weight'))
    return chargeable_weight


def all_fields_present(request):
    if (
        (request.get("origin_airport_id") is not None)
        and (request.get("destination_airport_id") is not None)
        and (request.get("commodity") is not None)
        and (request.get("airline_id") is not None)
        and (request.get("operation_type") is not None)
        and (request.get("service_provider_id") is not None)
        and (request.get("price_type") is not None)
    ):
        return True
    return False


def get_density_params(freight_object, required_weight, request):
    return {
        "freight_object": freight_object,
        "trade_type": request.get("trade_type"),
        "gross_weight": request.get("weight"),
        "gross_volume": request.get("volume"),
        "chargeable_weight": required_weight,
    }


def get_density_wise_rate(density_params):
    ratio = (
        density_params["gross_volume"]
        * AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO
        / density_params["gross_weight"]
    )
    density_weight = density_params["gross_weight"] / density_params["gross_volume"]
    if density_params["trade_type"] == AIR_TRADE_IMPORT_TYPE:
        low_density_lower_limit = AIR_IMPORTS_LOW_DENSITY_RATIO
        high_density_upper_limit = AIR_IMPORTS_HIGH_DENSITY_RATIO
    low_density_lower_limit = AIR_EXPORTS_LOW_DENSITY_RATIO
    high_density_upper_limit = AIR_EXPORTS_HIGH_DENSITY_RATIO

    if ratio > low_density_lower_limit:
        density_category = "low_density"

    elif (
        ratio <= high_density_upper_limit and density_params["chargeable_weight"] >= 100
    ):
        density_category = "high_density"

    density_category = "general"

    if density_category == density_params["freight_object"]["density_category"]:
        if density_category == "general" or (
            density_category == "low_density"
            and int(density_params["freight_object"]["min_density_weight"])
            == int(density_weight)
        ):
            return density_params["freight_object"]
        elif (
            density_category == "high_density"
            and density_params["freight_object"]["min_density_weight"] <= density_weight
            and density_params["freight_object"]["max_density_weight"] > density_weight
        ):
            return density_params["freight_object"]
        else:
            return None
    else:
        return None


def get_freight_object(freight_validity, request):
    start = datetime.strptime(
        freight_validity["validity_start"], "%Y-%m-%dT%H:%M:%S.%fz"
    ).date()
    end = datetime.strptime(
        freight_validity["validity_end"], "%Y-%m-%dT%H:%M:%S.%fz"
    ).date()

    if start <= request.get("validity_start").date():
        validity_start = request.get("validity_start")

    if end >= request.get("validity_end").date():
        validity_end = request.get("validity_end")

    if freight_validity["density_category"]:
        density_category = freight_validity["density_category"]
    else:
        density_category = "general"
    if freight_validity["min_density_weight"]:
        min_density_weight = freight_validity["min_density_weight"]
    else:
        min_density_weight = 0.0

    if freight_validity["max_density_weight"]:
        max_density_weight = freight_validity["max_density_weight"]
    else:
        max_density_weight = MAX_CARGO_LIMIT

    return {
        "validity_id": freight_validity["id"],
        "likes_count": freight_validity["likes_count"],
        "dislikes_count": freight_validity["dislikes_count"],
        "line_items": [],
        "density_category": density_category,
        "min_density_weight": min_density_weight,
        "max_density_weight": max_density_weight,
        "validity_start": datetime.strftime(validity_start, "%Y-%m-%d"),
        "validity_end": datetime.strftime(validity_end, "%Y-%m-%d"),
    }


def get_required_weight_slab(freight_validity, required_weight, request):
    all_weight_slabs = freight_validity["weight_slabs"]
    for weight_slab in all_weight_slabs:
        if (
            weight_slab["lower_limit"] <= required_weight
            and weight_slab["upper_limit"] > required_weight
        ):
            return weight_slab


def find_object(request):
    object = (
        AirFreightRate.select()
        .where(
            AirFreightRate.origin_airport_id == request.get("origin_airport_id"),
            AirFreightRate.destination_airport_id
            == request.get("destination_airport_id"),
            AirFreightRate.commodity == request.get("commodity"),
            AirFreightRate.commodity_type == request.get("commodity_type"),
            AirFreightRate.commodity_sub_type == request.get("commodity_type"),
            AirFreightRate.service_provider_id == request.get("service_provider_id"),
            AirFreightRate.airline_id == request.get("airline_id"),
            AirFreightRate.operation_type == request.get("operation_type"),
            AirFreightRate.shipment_type == request.get("shipment_type"),
            AirFreightRate.stacking_type == request.get("stacking_type"),
            AirFreightRate.price_type == request.get("price_type"),
            AirFreightRate.cogo_entity_id == request.get("cogo_entity_id"),
        )
        .first()
    )

    return object
