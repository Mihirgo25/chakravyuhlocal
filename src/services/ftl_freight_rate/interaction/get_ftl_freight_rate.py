import geopy.distance
from micro_services.client import maps
from fastapi import HTTPException
from configs.ftl_freight_rate_constants import *

def get_distance(cord1, cord2):
    coords_1 = cord1
    coords_2 = cord2
    return geopy.distance.geodesic(coords_1, coords_2).km

def get_ftl_freight_rate(origin_location_id :  None, destination_location_id: None, truck_type: None):
    input = {"filters": {"id": [origin_location_id, destination_location_id] }}
    origin_location_data = None
    destination_location_data = None
    location_data = maps.list_locations(input)
    if not location_data:
        raise HTTPException(status_code=500, detail="origin location or destination Location are invalid")
    location_data = location_data['list']
    for data in location_data:
        if data["id"] == origin_location_id:
            origin_location_data = data
        if data["id"] == destination_location_id:
            destination_location_data = data

    shipment_distance = None

    if not origin_location_data or not  destination_location_data:
        raise HTTPException(status_code=500, detail="origin location or destination Location are invalid")

    origin_country_code = origin_location_data.get('country_code') 
    destination_country_code = destination_location_data.get('country_code')

    if origin_country_code != destination_country_code and (destination_country_code not in INTERNATIONAL_COUNTRY_CODE_ZONE_MAPPING.get(origin_country_code) or origin_country_code not in INTERNATIONAL_COUNTRY_CODE_ZONE_MAPPING.get(destination_country_code)):
        raise HTTPException(status_code=500, detail = "origin and destination location pair are invalid for ftl service")

    origin_location_coordinate = tuple((origin_location_data["latitude"], origin_location_data["longitude"]))
    destination_location_coordinate = tuple((destination_location_data["latitude"], destination_location_data["longitude"]))
    shipment_distance = get_distance(origin_location_coordinate, destination_location_coordinate)


    print(shipment_distance)
    return {'distance' : shipment_distance}