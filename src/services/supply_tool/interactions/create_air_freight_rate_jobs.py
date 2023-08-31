from database.rails_db import get_most_searched_predicted_rates_for_fcl_freight_services
from micro_services.client import partner,maps
import copy
from datetime import datetime, timedelta
from services.supply_tool.models.air_freight_rate_jobs import AirFreightRateJobs
from services.supply_tool.models.air_freight_rate_jobs_mapping import AirFreightRateJobsMapping
from database.rails_db import get_most_searched_predicted_rates_for_fcl_freight_services
import copy

MAX_LIMIT = 1
PAGE_LIMIT = 50

def create_air_freight_rate_jobs(service='air_freight'):
    list_of_spot_search_data = build_most_spot_searched_data(service)

    for spot_search in list_of_spot_search_data:
        row = {
            'origin_airport_id': spot_search.get('origin_airport_id'),
            'destination_airport_id': spot_search.get('destination_airport_id'),
            'commodity': spot_search.get('commodity'),
            'status':'pending'
        }
        
        if not is_job_existing(row):
            job = AirFreightRateJobs.create(**row)
            
            jobs_mapping = {
                'job_id': job.id
            }

            AirFreightRateJobsMapping.create(**jobs_mapping)
        
        else:
            print("Job Already Present")

def is_job_existing(data):
    existing_job = AirFreightRateJobs.select().where(
            AirFreightRateJobs.origin_airport_id == data['origin_airport_id'],
            AirFreightRateJobs.destination_airport_id == data['destination_airport_id'],
            AirFreightRateJobs.commodity == data['commodity']
        ).order_by(AirFreightRateJobs.updated_at.desc()).first()

    if not existing_job:
        return False

    if existing_job.status == 'active':
        return True

    elif existing_job.updated_at + timedelta(days=30) > datetime.now():
        return True

    return False


def build_most_spot_searched_data():
    data = []
    limit = PAGE_LIMIT
    for batch in range(MAX_LIMIT):
        offset = batch*limit
        query_data = get_most_searched_predicted_rates_for_fcl_freight_services('air_freight',offset,limit)
        if query_data is None:
            break
        data += get_spot_data(query_data)

    return data

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

def build_most_spot_searched_data(service):
    data = []
    limit = PAGE_LIMIT
    for batch in range(MAX_LIMIT):
        offset = batch*limit
        query_data = get_most_searched_predicted_rates_for_fcl_freight_services(service,offset,limit)
        if query_data is None:
            break
        data += get_spot_data(query_data)

    return data