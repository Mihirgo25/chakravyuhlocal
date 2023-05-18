from services.haulage_freight_rate.models.haulage_freight_rate_rule_sets import (
    HaulageFreightRateRuleSet,
)
from services.haulage_freight_rate.models.haulage_freight_rate import (
    HaulageFreightRate,
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
    SERVICE_PROVIDER_ID,
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


def build_ftl_freight_rate(
    origin_location_id,
    destination_location_id,
    base_price,
    total_distance,
    currency,
    location_data_mapping,
    truck_and_commodity_data,
):
    line_items_data = [
        {
            "code": "BAS",
            "unit": "per_truck",
            "price": base_price,
            "remarks": [],
            "currency": currency,
        }
    ]

    create_params = {
        "origin_location_id": origin_location_id,
        "destination_location_id": destination_location_id,
        "origin_country_id": location_data_mapping[origin_location_id]["country_id"],
        "destination_country_id": location_data_mapping[destination_location_id][
            "country_id"
        ],
        "distance": total_distance,
        "line_items": line_items_data,
        "truck_type": truck_and_commodity_data["truck_type"],
        "commodity_type": truck_and_commodity_data["commodity_type"],
        "commodity_weight": truck_and_commodity_data["commodity_weight"],
        "service_provider_id": SERVICE_PROVIDER_ID,
        "origin_city_id": location_data_mapping[origin_location_id]["city_id"],
        "destination_city_id": location_data_mapping[destination_location_id][
            "city_id"
        ],
    }

    HaulageFreightRate.create(**create_params)

    return


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


def get_north_america_rates(commodity, load_type, container_count, ports_distance):
    final_data = {}
    final_data["distance"] = ports_distance
    final_data["currency"] = "USD"
    final_data["country_code"] = "US"

    wagon_lower_limit = (
        HaulageFreightRateRuleSet.select()
        .where(
            HaulageFreightRateRuleSet.commodity_class_type == commodity,
            HaulageFreightRateRuleSet.distance <= ports_distance,
            HaulageFreightRateRuleSet.train_load_type == load_type,
            HaulageFreightRateRuleSet.currency == "USD",
            HaulageFreightRateRuleSet.country_code == "US",
        )
        .order_by(HaulageFreightRateRuleSet.distance.desc())
        .execute()
    )

    wagon_upper_limit = (
        HaulageFreightRateRuleSet.select()
        .where(
            HaulageFreightRateRuleSet.commodity_class_type == commodity,
            HaulageFreightRateRuleSet.distance >= ports_distance,
            HaulageFreightRateRuleSet.train_load_type == load_type,
            HaulageFreightRateRuleSet.currency == "USD",
            HaulageFreightRateRuleSet.country_code == "US",
        )
        .order_by(HaulageFreightRateRuleSet.distance)
        .execute()
    )

    wagon_price_lower_limit = [model_to_dict(item) for item in wagon_lower_limit]
    wagon_price_upper_limit = [model_to_dict(item) for item in wagon_upper_limit]

    if len(wagon_price_lower_limit) == 0 or len(wagon_price_upper_limit) == 0:
        if len(wagon_price_lower_limit) == 0:
            price = (
                wagon_price_upper_limit[0]["base_price"]
                / wagon_price_upper_limit["distance"]
            ) * ports_distance

        else:
            price = (
                wagon_price_lower_limit[0]["base_price"]
                / wagon_price_lower_limit["distance"]
            ) * ports_distance

    else:
        limit1 = limit2 = ports_distance
        limit1 = ports_distance - wagon_price_lower_limit[0]["distance"]
        limit2 = wagon_price_upper_limit[0]["distance"] - ports_distance

        if limit1 >= limit2:
            price = wagon_price_upper_limit[0]["base_price"]
        else:
            price = wagon_price_lower_limit[0]["base_price"]

    price = price * container_count
    surcharge = 0.15 * price
    development_charges = 0.05 * price
    final_data["base_price"] = price + surcharge + development_charges

    return final_data


def get_europe_rates(commodity, load_type, container_count, ports_distance, wagon_type):
    final_data = {}
    final_data["distance"] = ports_distance
    final_data["currency"] = "EUR"
    final_data["country_code"] = "EU"

    wagon_upper_limit = (
        HaulageFreightRateRuleSet.select()
        .where(
            HaulageFreightRateRuleSet.commodity_class_type == commodity,
            HaulageFreightRateRuleSet.distance >= ports_distance,
            HaulageFreightRateRuleSet.train_load_type == load_type,
            HaulageFreightRateRuleSet.wagon_type == wagon_type,
            HaulageFreightRateRuleSet.currency == "EUR",
            HaulageFreightRateRuleSet.country_code == "EU",
        )
        .order_by(HaulageFreightRateRuleSet.distance)
        .execute()
    )

    wagon_price_upper_limit = [model_to_dict(item) for item in wagon_upper_limit]

    if len(wagon_price_upper_limit) == 0:
        final_data["base_price"] = 0
        return final_data

    price = wagon_price_upper_limit[0]["base_price"]
    price = price * container_count
    surcharge = 0.15 * price
    development_charges = 0.05 * price
    final_data["base_price"] = price + surcharge + development_charges

    return final_data
