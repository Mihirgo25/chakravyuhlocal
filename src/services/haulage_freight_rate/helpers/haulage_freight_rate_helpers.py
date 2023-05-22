from micro_services.client import maps
from fastapi import HTTPException


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

        return locations_data, location_category
