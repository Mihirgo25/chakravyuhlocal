from services.supply_tool.models.fcl_freight_rate_jobs import FclFreightRateJobs
from libs.json_encoder import json_encoder
import os
import uuid
import pandas as pd
from services.rate_sheet.interactions.upload_file import upload_media_file
import copy
from micro_services.client import partner,maps

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))

def list_fcl_freight_rate_jobs(filters = {}):
    query = get_query()

    query_data = json_encoder(list(query.dicts()))

    list_of_spot_search_data = map_id_to_location(query_data)

    csv_url_for_spot_search_data = build_csv_url_for_spot_search(list_of_spot_search_data)

    result =  {'list': list_of_spot_search_data, 'csv_link': csv_url_for_spot_search_data, 'count': len(list_of_spot_search_data)}

    return result


def get_query():
    query = FclFreightRateJobs.select().where(
        FclFreightRateJobs.status == 'active'
    )
    return query

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

def get_location_mapping(query_data):
    location_ids = []
    location_mapping = {}
    location_ids += list(set(map(lambda data:str(data['origin_port_id']), query_data)))
    location_ids += list(set(map(lambda data:str(data['destination_port_id']), query_data)))
    filter_location_ids = []
    for location_id in location_ids:
        filter_location_ids.append(copy.deepcopy(location_id))

    input = {
                "filters": {
                            "id": filter_location_ids,
                            "type": "seaport"
                        },
                "page_limit": len(query_data) * 2 + 1
            }

    list_of_location_data = maps.list_locations(input.copy())["list"]
    for location_data in list_of_location_data:
        location_mapping[location_data["id"]] = location_data

    return location_mapping

def map_id_to_location(query_data):
    location_mapping = get_location_mapping(query_data)

    for spot_search_data in query_data:
        spot_search_data['origin_port'] = location_mapping[str(spot_search_data['origin_port_id'])]['display_name']
        spot_search_data['destination_port'] = location_mapping[str(spot_search_data['destination_port_id'])]['display_name']
        del spot_search_data['origin_port_id']
        del spot_search_data['destination_port_id']

    return query_data
