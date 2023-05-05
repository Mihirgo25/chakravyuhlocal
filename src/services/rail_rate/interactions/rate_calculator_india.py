from services.rail_rate.models.rail_rates_india import RailRatesIndia
import geopy.distance
from micro_services.client import maps

def get_distance(cord1, cord2):
    coords_1 = cord1
    coords_2 = cord2
    return geopy.distance.geodesic(coords_1, coords_2).km

def rate_calculator(origin_location, destination_location, commodity, load_type, container_count):
    # how will it depend on shipping line
    input = {"filters":{"id":[origin_location, destination_location]}}
    data = maps.list_locations(input)
    if data:
        data = data["list"]
    for d in data:
        if d["id"] == origin_location:
            origin_location = (d["latitude"], d["longitude"])
        if d["id"] == destination_location:
            destination_location = (d["latitude"], d["longitude"])
    ports_distance = get_distance(origin_location,destination_location)
    query = RailRatesIndia.select().where(RailRatesIndia.distance <= ports_distance, RailRatesIndia.distance >=ports_distance-50)
    

    # what is other logic

    back = list(query.dicts())

    # main part will be how do i map the commodities


    #  after mapping of commodiesties all i have to do is mutiply it by container count

    if container_count>50:
        return

    return
