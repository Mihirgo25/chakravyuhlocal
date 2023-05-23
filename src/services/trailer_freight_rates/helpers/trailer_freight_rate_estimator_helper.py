from micro_services.client import maps
from libs.get_distance import get_distance


def get_estimated_distance(origin_location_id, destination_location_id):
    input = {"filters":{"id":[origin_location_id, destination_location_id]}}
    data = maps.list_locations(input)
    # data = maps.get_distance_matrix_valhalla(input)
    try:
        if data:
            data = data["list"]
        for d in data:
            if d["id"] == origin_location_id:
                origin_location = (d["latitude"], d["longitude"])
            if d["id"] == destination_location_id:
                destination_location = (d["latitude"], d["longitude"])
        distance = get_distance(origin_location,destination_location)
    except:
        distance = 250
    return distance