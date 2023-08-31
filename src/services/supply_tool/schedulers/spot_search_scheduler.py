from database.rails_db import get_most_searched_predicted_rates_for_fcl_freight_services
from services.supply_tool.interactions.create_fcl_freight_rate_jobs import create_fcl_freight_rate_jobs
from services.supply_tool.interactions.create_air_freight_rate_jobs import create_air_freight_rate_jobs
from database.rails_db import get_most_searched_predicted_rates_for_fcl_freight_services
from fastapi.encoders import jsonable_encoder
from libs.json_encoder import json_encoder
import copy

def spot_search_scheduler():

    services = ['fcl_freight', 'air_freight']
    
    for service in services:
        data = get_most_searched_predicted_rates_for_fcl_freight_services(service)
        data = get_spot_data(data)
        if service == 'fcl_freight':
            create_fcl_freight_rate_jobs(data, service)
        else:
            create_air_freight_rate_jobs(data, service)


def get_spot_data(list_of_spot_search_data):
    list_of_data = []
    for spot_search_data in list_of_spot_search_data:
        data = {
            'origin_airport_id': spot_search_data[0],
            'destination_airport_id': spot_search_data[1],
            'commodity': spot_search_data[2],
            'row_count': spot_search_data[3],
            'has_predicted_source': spot_search_data[4]
        }
        list_of_data.append(copy.deepcopy(data))

    return list_of_data