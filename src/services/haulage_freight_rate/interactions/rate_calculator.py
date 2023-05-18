from services.haulage_freight_rate.models.haulage_freight_rate_rule_sets import (
    HaulageFreightRateRuleSet,
)
from micro_services.client import maps
import services.haulage_freight_rate.interactions.rate_calculator as rate_calculator
from configs.rails_constants import (
    DESTINATION_TERMINAL_CHARGES_INDIA,
    CONTAINER_TYPE_CLASS_MAPPINGS,
    DEFAULT_PERMISSIBLE_CARRYING_CAPACITY,
    WAGON_CONTAINER_TYPE_MAPPINGS,
    WAGON_COMMODITY_MAPPING,
    WAGON_MAPPINGS,
)
from libs.get_distance import get_distance
from playhouse.postgres_ext import SQL
from playhouse.shortcuts import model_to_dict


POSSIBLE_LOCATION_CATEGORY = [
    "india",
    "china",
    "europe",
    "north_america",
    "generalized",
]


def get_distances(origin_location, destination_location, data):
    for d in data:
        if d["id"] == origin_location:
            origin_location = (d["latitude"], d["longitude"])
        if d["id"] == destination_location:
            destination_location = (d["latitude"], d["longitude"])
    coords_1 = origin_location
    coords_2 = destination_location
    return get_distance(coords_1, coords_2)


def get_container_and_commodity_type(commodity, container_type, location_category):
    commodity = CONTAINER_TYPE_CLASS_MAPPINGS[container_type][0]
    permissable_carrying_capacity = WAGON_MAPPINGS[WAGON_COMMODITY_MAPPING[commodity]][
        0
    ]["permissable_carrying_capacity"]
    return commodity, permissable_carrying_capacity


def list_haulage_freight_rate(
    origin_location, destination_location, commodity, container_count, container_type
):
    return


def get_railway_route(origin_location, destination_location):
    return


def get_country_filter(origin_location, destination_location):
    input = {"filters": {"id": [origin_location, destination_location]}}
    location_category = ""
    locations_data = maps.list_locations(input)["list"]
    if locations_data[0]["country_code"] != locations_data[1]["country_code"]:
        location_category = "generalized"

    if (
        locations_data[0]["country_code"] == "IN"
        and locations_data[1]["country_code"] == "IN"
    ):
        location_category = "india"

    if (
        locations_data[0]["country_code"] == "CN"
        and locations_data[1]["country_code"] == "CN"
    ):
        location_category = "china"

    return locations_data, location_category


def apply_surcharges(indicative_price):
    surcharge = 0.15 * indicative_price
    development_charges = 0.05 * indicative_price
    other_charges = development_charges + DESTINATION_TERMINAL_CHARGES_INDIA
    gst_charges = indicative_price * 0.05
    final_price = indicative_price + surcharge + other_charges + gst_charges
    return final_price


def haulage_rate_calculator(
    origin_location,
    destination_location,
    commodity,
    container_count=None,
    container_type=None,
    cargo_weight_per_container=None,
):
    response = {"success": False, "status_code": 200}

    locations_data, location_category = get_country_filter(
        origin_location, destination_location
    )

    if location_category not in POSSIBLE_LOCATION_CATEGORY:
        return response

    location_pair_distance = get_distances(
        origin_location, destination_location, locations_data
    )

    if container_count:
        load_type = "Wagon Load"
    else:
        load_type = "Train Load"

    commodity, permissable_carrying_capacity = get_container_and_commodity_type(
        commodity, container_type, location_category
    )

    haulage_freight_rate = list_haulage_freight_rate(
        origin_location,
        destination_location,
        commodity,
        container_count,
        container_type,
    )

    if haulage_freight_rate:
        response["success"] = True
        response["list"] = haulage_freight_rate
        return response

    route_data = get_railway_route(origin_location, destination_location)
    # route_distance = route_data['distance']
    # replace location_pair_distance with route_distance once route comes from vahalla

    query = HaulageFreightRateRuleSet.select(HaulageFreightRateRuleSet.base_price)

    final_data = getattr(rate_calculator, "get_{}_rates".format(location_category))(
        query,
        commodity,
        load_type,
        container_count,
        location_pair_distance,
        container_type,
        cargo_weight_per_container,
        permissable_carrying_capacity,
    )

    response["success"] = True
    response["list"] = final_data
    return response


def get_india_rates(
    query,
    commodity,
    load_type,
    container_count,
    location_pair_distance,
    container_type,
    cargo_weight_per_container,
    permissable_carrying_capacity,
):
    print(permissable_carrying_capacity)
    final_data = {}
    final_data["distance"] = location_pair_distance
    if not container_count:
        container_count = 50
        load_type = "Train Load"
    if container_count > 50:
        full_rake_count = container_count / 50
        remaining_wagons_count = container_count % 50
        rake_price = (
            query.where(
                HaulageFreightRateRuleSet.distance >= location_pair_distance,
                HaulageFreightRateRuleSet.commodity_class_type == commodity,
                HaulageFreightRateRuleSet.train_load_type == "Train Load",
            )
            .order_by(SQL("base_price ASC"))
            .first()
        )
        wagon_price = (
            query.where(
                HaulageFreightRateRuleSet.distance >= location_pair_distance,
                HaulageFreightRateRuleSet.commodity_class_type == commodity,
                HaulageFreightRateRuleSet.train_load_type == "Wagon Load",
            )
            .order_by(SQL("base_price ASC"))
            .first()
        )
        rake_price_per_tonne = model_to_dict(rake_price)["base_price"]
        wagon_price_per_tonne = model_to_dict(wagon_price)["base_price"]
        final_rake_price = (
            float(rake_price_per_tonne)
            * full_rake_count
            * 50
            * permissable_carrying_capacity
        )
        final_wagon_price = (
            float(wagon_price_per_tonne)
            * remaining_wagons_count
            * permissable_carrying_capacity
        )
        indicative_price = final_rake_price + final_wagon_price
        final_data["base_price"] = apply_surcharges(indicative_price)
    else:
        query = (
            query.where(
                HaulageFreightRateRuleSet.distance >= location_pair_distance,
                HaulageFreightRateRuleSet.commodity_class_type == commodity,
                HaulageFreightRateRuleSet.train_load_type == load_type,
            )
            .order_by(SQL("base_price ASC"))
            .first()
        )
        price = model_to_dict(query)
        price_per_tonne = price["base_price"]
        # permissible_carrying_capacity = WagonTypes.select(WagonTypes.permissible_carrying_capacity).where(WagonTypes.wagon_code == wagon_type)
        # price = float(price_per_tonne) * container_count * int(permissible_carrying_capacity.dicts().get()['permissible_carrying_capacity'])
        # else:

        indicative_price = (
            float(price_per_tonne) * container_count * permissable_carrying_capacity
        )
        final_data["base_price"] = apply_surcharges(indicative_price)

    final_data["currency"] = "INR"
    return final_data


def get_generalized_rates(
    query, commodity, load_type, container_count, location_pair_distance, container_type
):
    final_data = {}
    final_data["distance"] = location_pair_distance
    return


def get_china_rates(
    query, commodity, load_type, container_count, location_pair_distance, container_type
):
    final_data = {}
    final_data["distance"] = location_pair_distance
    return
