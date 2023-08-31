from services.supply_tool.models.air_freight_rate_jobs import AirFreightRateJobs
from libs.json_encoder import json_encoder
import os
import uuid
import pandas as pd
from services.rate_sheet.interactions.upload_file import upload_media_file
import copy
from micro_services.client import partner,maps

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))

def list_air_freight_rate_jobs():
    query = get_query()

    query_data = json_encoder(list(query.dicts()))

    list_of_spot_search_data  = mapping_id_to_location(query_data)
    
    csv_url_for_spot_search_data = build_csv_url_for_spot_search(list_of_spot_search_data)

    result =  {'list': list_of_spot_search_data, 'csv_link': csv_url_for_spot_search_data, 'count': len(list_of_spot_search_data)}

    return result

def build_csv_url_for_spot_search(list_of_spot_search_data):
    headers = ['id','origin_port','destination_port','container_size','container_type','commodity']

    file_path = os.path.join(ROOT_DIR,'tmp','fcl_spot_search_data')
    file_name = f'most_search_spot_data_{uuid.uuid4().hex}.csv'
    csv_file_path = os.path.join(file_path, file_name)
    os.makedirs(file_path, exist_ok=True)

    df = pd.DataFrame(list_of_spot_search_data, columns=headers)
    df.to_csv(csv_file_path)

    csv_url = upload_media_file(csv_file_path)

    return csv_url

def get_query():
    query = AirFreightRateJobs.select().where(
        AirFreightRateJobs.status == 'active'
    )
    return query

def mapping_id_to_location(query_data):
    location_ids = []
    location_mapping = {}
    location_ids += list(set(map(lambda data:str(data['origin_airport_id']), query_data)))
    location_ids += list(set(map(lambda data:str(data['destination_airport_id']), query_data)))
    filter_location_ids = []
    for location_id in location_ids:
        if location_mapping.get(location_id) is None:
            filter_location_ids.append(copy.deepcopy(location_id))

    input = {
                "filters": {
                            "id": filter_location_ids,
                            "type": "airport"
                        },
                "page_limit": len(query_data) * 2 + 1
            }
    list_of_location_data = maps.list_locations(input.copy())["list"]
    for location_data in list_of_location_data:
        location_mapping[location_data["id"]] = location_data

    return location_mapping