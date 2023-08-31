from database.rails_db import get_most_searched_predicted_rates_for_fcl_freight_services
from services.supply_tool.interactions.create_fcl_freight_rate_jobs import create_fcl_freight_rate_jobs
import copy

MAX_LIMIT = 1
PAGE_LIMIT = 5

def fcl_freight_rate_job_scheduler():
    list_of_spot_search_data = build_most_spot_searched_data()

    breakpoint()

    result = create_fcl_freight_rate_jobs(list_of_spot_search_data)

    return result

def build_most_spot_searched_data():
    data = []
    limit = PAGE_LIMIT
    for batch in range(MAX_LIMIT):
        offset = batch*limit
        query_data = get_most_searched_predicted_rates_for_fcl_freight_services("fcl_freight",offset,limit)
        if query_data is None:
            break
        data += get_spot_data(query_data)

    return data

def get_spot_data(list_of_spot_search_data):
    list_of_data = []
    for spot_search_data in list_of_spot_search_data:
        data = {
            'origin_port_id': spot_search_data[0],
            'destination_port_id': spot_search_data[1],
            'container_size': spot_search_data[2],
            'container_type': spot_search_data[3],
            'commodity': spot_search_data[4],
        }
        list_of_data.append(copy.deepcopy(data))

    return list_of_data
