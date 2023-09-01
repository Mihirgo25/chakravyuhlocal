from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.rate_sheet.interactions.upload_file import upload_media_file
from micro_services.client import maps
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
import os
import pandas as pd
from fastapi.encoders import jsonable_encoder
from datetime import datetime, timedelta
from services.bramhastra.client import ClickHouse
from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJobs
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_jobs import create_fcl_freight_rate_jobs
from services.air_freight_rate.interactions.create_air_freight_rate_jobs import create_air_freight_rate_jobs
import time 

def cancelled_shipments_scheduler():
    clickhouse = ClickHouse()
    services = ['fcl_freight', 'air_freight']
    required_columns = {
        'fcl_freight': ['rate_id', 'origin_port_id', 'origin_main_port_id', 'destination_port_id', 'destination_main_port_id',
                        'shipping_line_id', 'service_provider_id', 'container_size', 'container_type', 'commodity', 'rate_type'],
        'air_freight': ['rate_id', 'origin_airport_id','destination_airport_id','commodity', 'airline_id', 'service_provider_id', 'rate_type']
    }
    filters = {'end_date': datetime.today()-timedelta(7)}

    for service in services:
        select = ','.join(required_columns[service])
        query = f'''SELECT {select} from brahmastra.{service}_rate_statistics WHERE updated_at >= %(end_date)s'''
        results = jsonable_encoder(clickhouse.execute(query,filters))
        eval(f"create_{service}_rate_jobs")(results, 'cancelled_shipments')




