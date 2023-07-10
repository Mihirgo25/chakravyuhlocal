
from micro_services.client import maps
from libs.get_distance import get_distance
import httpx, json
from datetime import datetime
import dateutil.parser as parser

def get_land_route_from_valhalla(location_ids):
    params = {
        'location_ids': json.dumps(location_ids),
        'number_of_locations': '5',
        'is_authorization_required': 'false'
    }
    return maps.get_land_route_location_details(params)

def get_road_route(origin_location_id, destination_location_id):

    location_ids = [origin_location_id,destination_location_id]

    data = get_land_route_from_valhalla(location_ids)
    if isinstance(data, dict):
        return data
    return None

def convert_date_format(date):
    if not date:
        return date
    parsed_date = parser.parse(date, dayfirst=True)
    return datetime.strptime(str(parsed_date.date()), '%Y-%m-%d')


def get_transit_time(distance):
    transit_time = (distance / 250) * 24
    return transit_time


def get_path_data(origin_location_id, destination_location_id, location_data):
    route_distance = get_road_route(origin_location_id, destination_location_id)
    if route_distance:
        route_distance['time'] = route_distance['time']/3600
        route_distance['is_valhala'] = True
        return route_distance

    origin_location = (location_data[origin_location_id]["latitude"], location_data[origin_location_id]["longitude"])
    destination_location = (location_data[destination_location_id]["latitude"], location_data[destination_location_id]["longitude"])
    coords_1 = origin_location
    coords_2 = destination_location
    distance = get_distance(coords_1, coords_2)
    transit_time = get_transit_time(distance)
    location_details = []
    for location_ids  in [origin_location_id,destination_location_id]:
        for location_key in ['id','city_id','pincode_id','region_id','district_id','country_id']:
            if location_data[location_ids].get(location_key):
                location_details.append(location_data[location_ids][location_key])
    return {
        'location_details':location_details,
         'distance':distance,
         'time': transit_time,
         'is_valhala':False
    }
