from services.haulage_freight_rate.models.haulage_freight_rate_rule_sets import (
    HaulageFreightRateRuleSet,
)
from services.haulage_freight_rate.models.haulage_freight_rate import (
    HaulageFreightRate,
)
import datetime
from micro_services.client import maps
import services.haulage_freight_rate.interactions.get_haulage_freight_rate_estimation as get_haulage_freight_rate_estimation
from configs.rails_constants import (
    DESTINATION_TERMINAL_CHARGES_INDIA,
    CONTAINER_TYPE_CLASS_MAPPINGS,
    DEFAULT_PERMISSIBLE_CARRYING_CAPACITY,
    WAGON_CONTAINER_TYPE_MAPPINGS,
    WAGON_COMMODITY_MAPPING,
    WAGON_MAPPINGS,
    SERVICE_PROVIDER_ID,
    DEFAULT_HAULAGE_TYPE,
    DEFAULT_TRIP_TYPE,
)
from configs.global_constants import COGO_ENVISION_ID
from libs.get_distance import get_distance
from playhouse.postgres_ext import SQL
from playhouse.shortcuts import model_to_dict
from fastapi import HTTPException
from micro_services.client import maps


POSSIBLE_LOCATION_CATEGORY = [
    "india",
    "china",
    "europe",
    "north_america",
    "generalized",
]

def apply_surcharges_for_usa_europe(price):
    surcharge = 0.15 * price
    development_charges = 0.05 * price
    final_price = price + surcharge + development_charges

    return final_price


def get_distances(origin_location, destination_location, data):
    for d in data:
        if d["id"] == origin_location:
            origin_location = (d["latitude"], d["longitude"])
        if d["id"] == destination_location:
            destination_location = (d["latitude"], d["longitude"])
    coords_1 = origin_location
    coords_2 = destination_location
    # route_distance = get_railway_route(origin_location, destination_location)
    # if route_distance:
    #     return route_distance
    return get_distance(coords_1, coords_2)


def get_container_and_commodity_type(commodity, container_type, location_category):
    commodity = CONTAINER_TYPE_CLASS_MAPPINGS[container_type][0]
    permissable_carrying_capacity = WAGON_MAPPINGS[WAGON_COMMODITY_MAPPING[commodity]][
        0
    ]["permissable_carrying_capacity"]
    return commodity, permissable_carrying_capacity


def get_haulage_freight_rate(
    origin_location, destination_location, commodity, containers_count, container_type
):
    haulage_freight_rate = HaulageFreightRate.select(HaulageFreightRate.line_items).where(HaulageFreightRate.origin_location_id == origin_location, HaulageFreightRate.destination_location_id ==destination_location, HaulageFreightRate.commodity == commodity, HaulageFreightRate.containers_count == containers_count, HaulageFreightRate.container_type == container_type)
    if haulage_freight_rate.count()==0:
        return None
    rate = model_to_dict(haulage_freight_rate)
    final_data = {}
    final_data["base_price"] = rate['line_items']['price']
    distance = rate['distance']
    final_data["currency"] = rate['line_items']['currency']
    final_data["upper_limit"] = 10
    final_data["transit_time"] = get_transit_time(distance)
    return [final_data]


def get_railway_route(origin_location, destination_location):
    input = {"origin_location_id": origin_location, "destination_location_id": destination_location}
    try:
        data = maps.get_distance_matrix_valhalla(input)
    except HTTPException as e:
        data = None
    return data

def get_transit_time(distance):
    transit_time = (distance//250) * 24
    if transit_time == 0:
        transit_time = 12
    return transit_time


def get_country_filter(origin_location, destination_location):
    input = {"filters": {"id": [origin_location, destination_location]}}
    location_category = "generalized"
    locations_data = maps.list_locations(input)["list"]
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


def build_haulage_freight_rate(
    origin_location_id,
    destination_location_id,
    base_price,
    distance,
    currency,
    container_size,
    container_type,
    containers_count,
    commodity
):
    line_items_data = [
        {
            "code": "BAS",
            "unit": "per_container",
            "price": base_price,
            "remarks": [],
            "slabs": [],
            "currency": currency,
        }
    ]

    create_params = {
        "origin_location_id": origin_location_id,
        "destination_location_id": destination_location_id,
        "container_size": container_size,
        "container_type": container_type,
        "containers_count": containers_count,
        "commodity": commodity,
        "service_provider_id": SERVICE_PROVIDER_ID,
        "haulage_type": DEFAULT_HAULAGE_TYPE,
        "performed_by_id": COGO_ENVISION_ID,
        "procured_by_id": COGO_ENVISION_ID,
        "sourced_by_id": COGO_ENVISION_ID,
        "transport_modes": ["rail"],
        "transport_modes_keyword": "rail",
        "line_items": line_items_data,
        "trip_type": DEFAULT_TRIP_TYPE,
        "distance": distance,
        "validity_start": datetime.datetime.now(),
        "validity_end": datetime.datetime.now() + datetime.timedelta(days=60),
    }
    return create_params


def create_haulage_freight_rate(create_params):
    HaulageFreightRate.create(**create_params)
    return


def haulage_rate_calculator(request):
    from celery_worker import create_haulage_freight_rate_delay

    origin_location = request.origin_location_id
    destination_location = request.destination_location_id
    commodity = request.commodity
    containers_count = request.containers_count
    container_type = request.container_type
    cargo_weight_per_container = request.cargo_weight_per_container
    container_size = request.container_size

    response = {"success": False, "status_code": 200}

    haulage_freight_rate = get_haulage_freight_rate(
        origin_location,
        destination_location,
        commodity,
        containers_count,
        container_type,
    )

    if haulage_freight_rate:
        response["success"] = True
        response["list"] = haulage_freight_rate
        return response

    locations_data, location_category = get_country_filter(
        origin_location, destination_location
    )

    if location_category not in POSSIBLE_LOCATION_CATEGORY:
        return response

    location_pair_distance = get_distances(
        origin_location, destination_location, locations_data
    )

    if containers_count:
        load_type = "Wagon Load"
    else:
        load_type = "Train Load"

    commodity, permissable_carrying_capacity = get_container_and_commodity_type(
        commodity, container_type, location_category
    )


    query = HaulageFreightRateRuleSet.select(
        HaulageFreightRateRuleSet.base_price,
        HaulageFreightRateRuleSet.running_base_price,
        HaulageFreightRateRuleSet.currency,
    )
    final_data = getattr(get_haulage_freight_rate_estimation, "get_{}_rates".format(location_category))(
        query,
        commodity,
        load_type,
        containers_count,
        location_pair_distance,
        container_type,
        cargo_weight_per_container,
        permissable_carrying_capacity,
        container_size,
    )

    params = build_haulage_freight_rate(
        origin_location,
        destination_location,
        final_data["base_price"],
        location_pair_distance,
        final_data["currency"],
        container_size,
        container_type,
        containers_count,
        commodity
    )
    create_haulage_freight_rate_delay.apply_async(kwargs = {'params' : params} , queue='low')
    response["success"] = True
    response["list"] = [final_data]
    return response


def get_india_rates(
    query,
    commodity,
    load_type,
    containers_count,
    location_pair_distance,
    container_type,
    cargo_weight_per_container,
    permissable_carrying_capacity,
    container_size,
):
    final_data = {}
    final_data["distance"] = location_pair_distance
    if not containers_count:
        containers_count = 1
        load_type = "Wagon Load"
    if containers_count > 50:
        full_rake_count = containers_count / 50
        remaining_wagons_count = containers_count % 50
        rake_price = (
            query.where(
                HaulageFreightRateRuleSet.distance >= location_pair_distance,
                HaulageFreightRateRuleSet.commodity_class_type == commodity,
                HaulageFreightRateRuleSet.train_load_type == "Train Load",
            )
            .order_by(SQL("base_price ASC"))
        )
        wagon_price = (
            query.where(
                HaulageFreightRateRuleSet.distance >= location_pair_distance,
                HaulageFreightRateRuleSet.commodity_class_type == commodity,
                HaulageFreightRateRuleSet.train_load_type == "Wagon Load",
            )
            .order_by(SQL("base_price ASC"))
        )
        if rake_price.count()==0 or wagon_price.count()==0 :
            raise HTTPException(status_code=400, detail="rates not present")
        rake_price_per_tonne = model_to_dict(rake_price.first())["base_price"]
        wagon_price_per_tonne = model_to_dict(wagon_price.first())["base_price"]

        if not rake_price_per_tonne or not wagon_price_per_tonne:
            raise HTTPException(status_code=400, detail="rates not present")

        currency = model_to_dict(wagon_price)["currency"]
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
        )
        if query.count()==0:
            raise HTTPException(status_code=400, detail="rates not present")

        price = model_to_dict(query.first())
        price_per_tonne = price["base_price"]
        currency = price["currency"]

        indicative_price = (
            float(price_per_tonne) * containers_count * permissable_carrying_capacity
        )
        final_data["base_price"] = apply_surcharges(indicative_price)

    final_data["currency"] = currency
    final_data["upper_limit"] = 10
    final_data["transit_time"] = get_transit_time(location_pair_distance)

    return final_data


def get_china_rates(
    query,
    commodity,
    load_type,
    containers_count,
    location_pair_distance,
    container_type,
    cargo_weight_per_container,
    permissable_carrying_capacity,
    container_size,
):
    final_data = {}
    final_data["distance"] = location_pair_distance
    query = (
        query.where(
            HaulageFreightRateRuleSet.container_type == container_size,
            HaulageFreightRateRuleSet.train_load_type == load_type,
        )
        .order_by(SQL("base_price ASC"))
    )

    if query.count()==0:
        raise HTTPException(status_code=400, detail="rates not present")
    price = model_to_dict(query.first())
    currency = price["currency"]
    price_per_container = float(price["base_price"])
    running_base_price_per_carton_km = float(price["running_base_price"])
    base_price = price_per_container * containers_count
    running_base_price = (
        running_base_price_per_carton_km
        * cargo_weight_per_container
        * float(location_pair_distance)
    )
    indicative_price = base_price + running_base_price
    final_data["base_price"] = apply_surcharges(indicative_price)
    final_data["currency"] = currency
    final_data["upper_limit"] = 10
    final_data["transit_time"] = get_transit_time(location_pair_distance)
    return final_data


def get_north_america_rates(commodity, load_type, container_count, ports_distance):
    final_data = {}
    final_data["distance"] = ports_distance
    final_data["currency"] = "USD"
    final_data["country_code"] = "US"

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
    )

    wagon_price_upper_limit = [model_to_dict(item) for item in wagon_upper_limit]

    if not wagon_price_upper_limit:
        raise HTTPException(status_code=400, detail="rates not present")


    price = wagon_price_upper_limit[0]["base_price"]
    price = price * container_count
    final_data["base_price"] = apply_surcharges_for_usa_europe(float(price))

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
    )
    wagon_price_upper_limit = [model_to_dict(item) for item in wagon_upper_limit]

    if not wagon_price_upper_limit:
        raise HTTPException(status_code=400, detail="rates not present")

    price = wagon_price_upper_limit[0]["base_price"]
    price = price * container_count
    final_data["base_price"] = apply_surcharges_for_usa_europe(float(price))

    return final_data


def get_generalized_rates(
    query,
    commodity,
    load_type,
    containers_count,
    location_pair_distance,
    container_type,
    cargo_weight_per_container,
    permissable_carrying_capacity,
    container_size,
):
    final_data = {}
    final_data["distance"] = location_pair_distance
    raise HTTPException(status_code=400, detail="rates not present")
