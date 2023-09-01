from database.rails_db import get_most_searched_predicted_rates_for_fcl_freight_services
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_jobs import create_fcl_freight_rate_jobs
from services.air_freight_rate.interactions.create_air_freight_rate_jobs import create_air_freight_rate_jobs
from database.rails_db import get_most_searched_predicted_rates_for_fcl_freight_services
from fastapi.encoders import jsonable_encoder
from libs.json_encoder import json_encoder
import copy

def spot_search_scheduler():

    services = ['fcl_freight', 'air_freight']

    for service in services:
        data = get_most_searched_predicted_rates_for_fcl_freight_services(service)
        if service == 'fcl_freight':
            data = get_spot_data_fcl(data)
            result = create_fcl_freight_rate_jobs(data, 'spot_search')
        else:
            data = get_spot_data_air(data)
            result = create_air_freight_rate_jobs(data, 'spot_search')

def get_spot_data_air(list_of_spot_search_data):
    list_of_data = []
    for spot_search_data in list_of_spot_search_data:
        data = {
            'origin_airport_id': spot_search_data[0],
            'destination_airport_id': spot_search_data[1],
            'commodity': spot_search_data[2],
            'airline_id': spot_search_data[3],
            'service_provider_id': spot_search_data[4]
        }
        list_of_data.append(copy.deepcopy(data))

    return list_of_data

def get_spot_data_fcl(list_of_spot_search_data):
    list_of_data = []
    for spot_search_data in list_of_spot_search_data:
        data = {
            'origin_port_id': spot_search_data[0],
            'destination_port_id': spot_search_data[1],
            'container_size': spot_search_data[2],
            'container_type': spot_search_data[3],
            'commodity': spot_search_data[4],
            'shipping_line_id': spot_search_data[5],
            'service_provider_id': spot_search_data[6]
        }
        list_of_data.append(copy.deepcopy(data))

    return list_of_data
