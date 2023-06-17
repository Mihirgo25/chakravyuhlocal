from micro_services.client import maps
from fastapi import HTTPException
from libs.get_distance import get_distance


def get_railway_route(origin_location_id, destination_location_id):
    input = {
        "origin_location_id": origin_location_id,
        "destination_location_id": destination_location_id,
    }
    data = maps.get_distance_matrix_valhalla(input)
    if isinstance(data, dict):
        return data
    return None


def get_transit_time(distance):
    transit_time = (distance / 750) * 24
    return transit_time


def get_country_filter(origin_location, destination_location):
    if origin_location == destination_location:
        raise HTTPException(
            status_code=400,
            detail="origin_location_id cannot be same as destination_location_id",
        )
    input = {"filters": {"id": [origin_location, destination_location]}}
    location_category = "generalized"
    locations_data = maps.list_locations(input)["list"]
    if (
        locations_data[0]["country_code"] == "IN"
        and locations_data[-1]["country_code"] == "IN"
    ):
        location_category = "india"

    if (
        locations_data[0]["country_code"] == "CN"
        and locations_data[-1]["country_code"] == "CN"
    ):
        location_category = "china"

    if (
        locations_data[0]["country_code"] == "VN"
        and locations_data[-1]["country_code"] == "VN"
    ):
        location_category = "vietnam"

    if locations_data[0]["country_code"] in [
        "FR",
        "NO",
        "NL",
        "DE",
        "CH",
    ] and locations_data[-1]["country_code"] in [
        "FR",
        "NO",
        "NL",
        "DE",
        "CH",
    ]:
        location_category = "europe"

    if locations_data[0]["country_code"] in ["US", "CA", "MX"] and locations_data[-1][
        "country_code"
    ] in ["US", "CA", "MX"]:
        location_category = "north_america"
    if locations_data[0]["country_code"] in [
        "BO",
        "AG",
        "CL",
        "BR",
    ] and locations_data[-1]["country_code"] in [
        "BO",
        "AG",
        "CL",
        "BR",
    ]:
        location_category = "south_america"
    country_code = locations_data[0]["country_code"]
    return locations_data, location_category, country_code


def build_line_item(
    origin_location_id,
    destination_location_id,
    base_price,
    currency,
    locations_data,
    upper_limit,
):
    origin_is_icd = ""
    destination_is_icd = ""
    for data in locations_data:
        if data["id"] == origin_location_id:
            origin_is_icd = data["is_icd"]
        if data["id"] == destination_location_id:
            destination_is_icd = data["is_icd"]
    if destination_is_icd:
        line_item_code = "IHI"
    elif origin_is_icd:
        line_item_code = "IHE"
    else:
        line_item_code = "RAF"
    line_items_data = [
        {
            "code": line_item_code,
            "unit": "per_container",
            "price": base_price,
            "remarks": [],
            "slabs": [
                {
                    "price": base_price,
                    "lower_limit": 0,
                    "upper_limit": upper_limit,
                    "currency": currency,
                }
            ],
            "currency": currency,
        }
    ]
    return line_items_data


def get_distances(origin_location_id, destination_location_id, data):
    route_distance = get_railway_route(origin_location_id, destination_location_id)
    if route_distance:
        distance = route_distance.get("distance")
        time = route_distance.get("time")
        if distance and time:
            return distance, time / 3600
    for d in data:
        if d["id"] == origin_location_id:
            origin_location = (d["latitude"], d["longitude"])
        if d["id"] == destination_location_id:
            destination_location = (d["latitude"], d["longitude"])
    coords_1 = origin_location
    coords_2 = destination_location
    distance = get_distance(coords_1, coords_2)
    transit_time = get_transit_time(distance)
    return distance, transit_time
