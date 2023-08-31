from database.rails_db import get_most_searched_predicted_rates_for_fcl_freight_services
from micro_services.client import partner,maps
import copy
from services.supply_tool.models.fcl_freight_rate_jobs import FclFreightRateJobs
from services.supply_tool.models.fcl_freight_rate_jobs_mapping import FclFreightRateJobsMapping
from datetime import datetime, timedelta

MAX_LIMIT = 1
PAGE_LIMIT = 5

def create_fcl_freight_rate_jobs(service='fcl_freight'):
    list_of_spot_search_data = build_most_spot_searched_data(service)

    ## PENDING - WHERE TO GET ALL COLUMNS?

    for spot_search in list_of_spot_search_data:
        row = {
            'origin_port_id': spot_search.get('origin_port_id'),
            'destination_port_id': spot_search.get('destination_port_id'),
            'container_size': spot_search.get('container_size'),
            'container_type': spot_search.get('container_type'),
            'commodity': spot_search.get('commodity'),
            'status':'active'
        }

        if not is_job_existing(row):
            job = FclFreightRateJobs.create(**row)
            print(job.id)

            mapping_row = {
                'job_id': job.id
            }
            mapping = FclFreightRateJobsMapping.create(**mapping_row)
            print(mapping.id)

        else:
            print("Jobs Already Present")

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

def is_job_existing(data):
    existing_job = FclFreightRateJobs.select().where(
            FclFreightRateJobs.origin_port_id == data['origin_port_id'],
            FclFreightRateJobs.destination_port_id == data['destination_port_id'],
            FclFreightRateJobs.container_size == data['container_size'],
            FclFreightRateJobs.container_type == data['container_type'],
            FclFreightRateJobs.commodity == data['commodity']
        ).order_by(FclFreightRateJobs.updated_at.desc()).first()

    if not existing_job: ## if jobs does not exist
        return False

    if existing_job.status == 'active':  ## if jobs exists and active
        return True

    elif existing_job.updated_at + timedelta(days=30) > datetime.now():  ## if jobs exists and updated within 1 month
        return True

    return False
