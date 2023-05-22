from micro_services.client import maps
from fastapi import HTTPException
from libs.get_distance import get_distance


def get_railway_route(origin_location_id, destination_location_id):
    input = {
        "origin_location_id": origin_location_id,
        "destination_location_id": destination_location_id,
    }
    try:
        data = maps.get_distance_matrix_valhalla(input)
    except HTTPException as e:
        data = None
    return data

def get_transit_time(distance):
    transit_time = (distance // 250) * 24
    if transit_time == 0:
        transit_time = 12
    return transit_time


def get_country_filter( origin_location, destination_location):
        input = {"filters": {"id": [origin_location, destination_location]}}
        location_category = "generalized"
        print(input)
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

        if (
            locations_data[0]["country_code"] in ["FR", "NO", "NL", "DE", "CH"]
            and locations_data[1]["country_code"] in ["FR", "NO", "NL", "DE", "CH"]
        ):
            location_category = "europe"

        if (
            locations_data[0]["country_code"] in ["US", "CA", "MX"]
            and locations_data[1]["country_code"] in ["US", "CA", "MX"]
        ):
            location_category = "north_america"

        return locations_data, location_category




def build_line_item(
    origin_location_id, destination_location_id, base_price, currency, locations_data
):
    origin_location_type = ""
    destination_location_type = ""
    for data in locations_data:
        if data["id"] == origin_location_id:
            origin_location_type = data["type"]
        if data["id"] == destination_location_id:
            destination_location_type = data["type"]
    if origin_location_type == "seaport":
        line_item_code = "IHI"
    elif destination_location_type == "seaport":
        line_item_code = "IHE"
    else:
        line_item_code = "BAS"
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
