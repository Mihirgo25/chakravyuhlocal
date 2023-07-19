from micro_services.client import maps
from fastapi import HTTPException
from libs.get_distance import get_distance
from database.db_session import rd
from libs.parse_numeric import parse_numeric
from micro_services.client import organization
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
processed_percent_hash = "process_percent_haulage_operation"


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

def get_progress_percent(id, progress = 0):
    progress_percent_hash = "process_percent_haulage_operation"
    progress_percent_key =  f"haulage_rate_bulk_operation_{id}"
    
    if rd:
        try:
            cached_response = rd.hget(progress_percent_hash, progress_percent_key)
            return max(parse_numeric(cached_response) or 0, progress)
        except:
            return progress
    else: 
        return progress

def adding_multiple_service_object(haulage_object,request):
    from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
    if not HaulageFreightRate.select().where(HaulageFreightRate.service_provider_id==request["service_provider_id"], HaulageFreightRate.rate_not_available_entry==False).exists():
        organization.update_organization({'id':request.get("service_provider_id"), "freight_rates_added":True})
    get_multiple_service_objects(haulage_object)

    
def processed_percent_key(self, id):
    return f"haulage_rate_bulk_operation_{id}"

def set_processed_percent_haulage_operation(processed_percent, id):
    if rd:
        rd.hset(processed_percent_hash, processed_percent_key(id), processed_percent)