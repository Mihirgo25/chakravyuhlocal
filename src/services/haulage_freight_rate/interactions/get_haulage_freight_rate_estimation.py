from services.haulage_freight_rate.models.haulage_freight_rate import (
    HaulageFreightRate,
)
from playhouse.shortcuts import model_to_dict
from configs.global_constants import COGO_ENVISION_ID
import datetime
from configs.haulage_freight_rate_constants import (
    SERVICE_PROVIDER_ID,
    DEFAULT_HAULAGE_TYPE,
    DEFAULT_TRIP_TYPE,
)
from libs.get_distance import get_distance

from services.haulage_freight_rate.models.haulage_freight_rate_rule_sets import (
    HaulageFreightRateRuleSet,
)
from services.haulage_freight_rate.rate_estimators.haulge_freight_rate_estimator import HaulageFreightRateEstimator

from services.haulage_freight_rate.helpers.haulage_freight_rate_helpers import get_transit_time, get_country_filter

POSSIBLE_LOCATION_CATEGORY = [
    "india",
    "china",
    "europe",
    "north_america",
    "generalized",
]

def get_haulage_freight_rate(
    origin_location, destination_location, containers_count, container_type, container_size
):
    haulage_freight_rate = HaulageFreightRate.select(HaulageFreightRate.line_items, HaulageFreightRate.distance).where(HaulageFreightRate.origin_location_id == origin_location, HaulageFreightRate.destination_location_id ==destination_location, HaulageFreightRate.containers_count == containers_count, HaulageFreightRate.container_type == container_type, HaulageFreightRate.container_size == container_size)
    if haulage_freight_rate.count()==0:
        return None
    rate = model_to_dict(haulage_freight_rate.first())
    final_data = {}
    final_data["base_price"] = rate['line_items'][0]['price']
    distance = rate['distance']
    final_data["currency"] = rate['line_items'][0]['currency']
    final_data["transit_time"] = get_transit_time(distance)
    final_data['line_items'] = rate['line_items']
    return [final_data]


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

def build_line_item(origin_location_id, destination_location_id, base_price, currency, locations_data):
    origin_location_type = ''
    destination_location_type = ''
    for data in locations_data:
        if data['id'] == origin_location_id:
            origin_location_type = data['type']
        if data['id'] == destination_location_id:
            destination_location_type = data['type']
    if origin_location_type == 'seaport':
        line_item_code = 'IHI'
    elif destination_location_type == 'seaport':
        line_item_code = 'IHE'
    else:
        line_item_code = 'BAS'
    line_items_data = [
        {
            "code": line_item_code,
            "unit": "per_container",
            "price": base_price,
            "remarks": [],
            "slabs": [],
            "currency": currency,
        }
    ]
    return line_items_data


def build_haulage_freight_rate(
    origin_location_id,
    destination_location_id,
    base_price,
    distance,
    currency,
    container_size,
    container_type,
    containers_count,
    commodity,
    locations_data
):
    line_items_data = build_line_item(origin_location_id, destination_location_id, base_price, currency, locations_data)

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
    return line_items_data, create_params


def create_haulage_freight_rate(create_params):
    HaulageFreightRate.create(**create_params)
    return



def haulage_rate_calculator(request):

    origin_location = request.origin_location_id
    destination_location = request.destination_location_id
    commodity = request.commodity
    containers_count = request.containers_count
    container_type = request.container_type
    cargo_weight_per_container = request.cargo_weight_per_container
    container_size = request.container_size

    response = {"success": False, "status_code": 200}

    locations_data, location_category = get_country_filter(
        origin_location, destination_location
    )
    if location_category not in POSSIBLE_LOCATION_CATEGORY:
        return response

    location_pair_distance = get_distances(
        origin_location, destination_location, locations_data
    )

    if not containers_count:
        containers_count = 1
        load_type = "Wagon Load"

    haulage_freight_rate = get_haulage_freight_rate(
        origin_location,
        destination_location,
        containers_count,
        container_type,
        container_size
    )

    if haulage_freight_rate:
        response["success"] = True
        response["list"] = haulage_freight_rate
        return response


    if containers_count:
        load_type = "Wagon Load"
    else:
        load_type = "Train Load"



    query = HaulageFreightRateRuleSet.select(
        HaulageFreightRateRuleSet.base_price,
        HaulageFreightRateRuleSet.running_base_price,
        HaulageFreightRateRuleSet.currency,
    )
    final_data_object = HaulageFreightRateEstimator(
        query,
        commodity,
        load_type,
        containers_count,
        container_type,
        cargo_weight_per_container,
        container_size,
        location_category
    )
    final_data = final_data_object.estimate()

    line_items_data, params = build_haulage_freight_rate(
        origin_location,
        destination_location,
        final_data["base_price"],
        location_pair_distance,
        final_data["currency"],
        container_size,
        container_type,
        containers_count,
        commodity,
        locations_data
    )
    final_data['line_items'] = line_items_data
    create_haulage_freight_rate(params)
    response["success"] = True
    response["list"] = [final_data]
    return response
