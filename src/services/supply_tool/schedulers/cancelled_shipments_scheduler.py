from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.rate_sheet.interactions.upload_file import upload_media_file
from micro_services.client import maps
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
import os
import pandas as pd
from fastapi.encoders import jsonable_encoder
from datetime import datetime, timedelta
from services.bramhastra.client import ClickHouse
from services.supply_tool.models.fcl_freight_rate_jobs import FclFreightRateJobs
from services.supply_tool.helpers.add_service_objects import add_service_objects
import time 

def cancelled_shipments_scheduler():
    shipments_data = get_cancelled_shipments()


def get_cancelled_shipments():
    clickhouse = ClickHouse()

    services = ['fcl_freight', 'air_freight']
    required_columns = {
        'fcl_freight': ['rate_id', 'origin_port_id', 'origin_main_port_id', 'destination_port_id', 'destination_main_port_id',
                        'shipping_line_id', 'service_provider_id', 'container_size', 'container_type', 'commodity']
    }
    
    filters = {'limit': 100, 'end_date': datetime.today()-timedelta(30)}
    for service in services:
        query = f'''SELECT {required_columns['service']} from brahmastra.{service}_rate_statistics WHERE updated_at >= %(end_date)s LIMIT %(limit)s'''
        results = jsonable_encoder(clickhouse.execute(query,filters))
        add_service_objects(results)
        create_jobs(service, results)

def create_jobs(service, results):
    
    for result in results:
        result['source'] = 'cancelled'
        result['status'] = 'active'
        result['assigned_to_id'] = ''
        result['assigned_to'] = ''

        find_jobs = FclFreightRateJobs.select()

