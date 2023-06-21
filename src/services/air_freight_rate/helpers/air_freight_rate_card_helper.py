from configs.air_freight_rate_constants import (
    AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO,
    AIR_IMPORTS_LOW_DENSITY_RATIO,
    AIR_IMPORTS_HIGH_DENSITY_RATIO,
    AIR_EXPORTS_LOW_DENSITY_RATIO,
    AIR_EXPORTS_HIGH_DENSITY_RATIO,
)
from configs.global_constants import MAX_VALUE


def get_density_wise_rate_card(
    response_object, trade_type, gross_weight, gross_volume, chargeable_weight
):
    ratio = round(
        (
            (gross_volume * AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO)
            / float(gross_weight)
        ),
        4,
    )
    density_rate_present = False
    density_rate_category = "general"
    density_weight = round(float(gross_weight) / (gross_volume), 2)
    if trade_type == "import":
        low_density_lower_limit = AIR_IMPORTS_LOW_DENSITY_RATIO
        high_density_upper_limit = AIR_IMPORTS_HIGH_DENSITY_RATIO
    else:
        low_density_lower_limit = AIR_EXPORTS_LOW_DENSITY_RATIO
        high_density_upper_limit = AIR_EXPORTS_HIGH_DENSITY_RATIO
    freights = []
    if ratio > low_density_lower_limit:
        closest_density_match = {}
        minimum_possible = MAX_VALUE
        density_rate_category = "low_density"
        for freight in response_object["freights"]:
            density_difference = abs(
                int(freight["min_density_weight"]) - int(density_weight)
            )
            if (
                int(freight["min_density_weight"]) == int(density_weight)
                and freight["density_category"] == "low_density"
            ):
                density_rate_present = True
                freights.append(freight)
            elif (
                density_difference < minimum_possible
                and freight["density_category"] == "low_density"
            ):
                minimum_possible = density_difference
                closest_density_match = freight
        if closest_density_match:
            freights.append(closest_density_match)
    elif ratio <= high_density_upper_limit and chargeable_weight >= 100:
        density_rate_category = "high_density"
        for freight in response_object["freights"]:
            if (
                freight["min_density_weight"] <= density_weight
                and freight["max_density_weight"] > density_weight
                and freight["density_category"] == "high_density"
            ):
                density_rate_present = True
                freights.append(freight)
            elif freight["density_category"] == "general":
                freights.append(freight)
    else:
        for freight in response_object["freights"]:
            if freight["density_category"] == "general":
                freights.append(freight)

    if density_rate_category == "high_density" and density_rate_present:
        freights = [
            freight_object
            for freight_object in freights
            if freight_object["density_category"] == "general"
        ]

    if not freights:
        return {}

    response_object["freights"] = freights

    return response_object
