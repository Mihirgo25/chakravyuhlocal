from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_job import create_fcl_freight_rate_job
import datetime
from playhouse.postgres_ext import ServerSide
from playhouse.shortcuts import model_to_dict

DAYS_TO_EXPIRE = datetime.datetime.now().date() + datetime.timedelta(days=7)

def fcl_freight_expiring_rates_scheduler():

    required_columns = ['id', 'origin_port_id', 'origin_port', 'origin_main_port_id', 'destination_port_id', 'destination_port','destination_main_port_id',
                        'shipping_line_id', 'shipping_line', 'service_provider_id', 'service_provider','container_size', 'container_type', 'commodity', 'rate_type','last_rate_available_date']
    
    fcl_query = FclFreightRate.select(*[getattr(FclFreightRate, col) for col in required_columns]).where(FclFreightRate.last_rate_available_date <= DAYS_TO_EXPIRE, FclFreightRate.mode.not_in(['predicted', 'cluster_extension']), FclFreightRate.rate_type != 'cogo_assured')

    for rate in ServerSide(fcl_query):
        rate_data = model_to_dict(rate)
        create_fcl_freight_rate_job(rate_data, 'expiring_rates')
        