from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.interactions.create_air_freight_rate_job import create_air_freight_rate_job
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_job import create_fcl_freight_rate_job
import datetime
from playhouse.postgres_ext import ServerSide
from playhouse.shortcuts import model_to_dict

DAYS_TO_EXPIRE = datetime.datetime.now().date() + datetime.timedelta(days=7)

def expiring_rates_scheduler():
    services = ['fcl_freight', 'air_freight']

    required_columns = {
        'fcl_freight': ['id', 'origin_port_id', 'origin_port', 'origin_main_port_id', 'destination_port_id', 'destination_port','destination_main_port_id',
                        'shipping_line_id', 'shipping_line', 'service_provider_id', 'service_provider','container_size', 'container_type', 'commodity', 'rate_type','last_rate_available_date'],
        'air_freight': ['id', 'origin_airport_id', 'origin_airport','destination_airport_id', 'destination_airport','commodity', 'airline_id', 'service_provider_id', 'rate_type', 'commodity_type', 'commodity_sub_type', 'operation_type', 'shipment_type', 'stacking_type', 'price_type']
    }
    
    for service in services:
        if service == "fcl_freight":
            fcl_query = FclFreightRate.select(*[getattr(FclFreightRate, col) for col in required_columns['fcl_freight']]).where(FclFreightRate.last_rate_available_date <= DAYS_TO_EXPIRE, FclFreightRate.mode.not_in(['predicted', 'cluster_extension']), FclFreightRate.rate_type != 'cogo_assured')
        if service == 'air_freight':
            air_query = AirFreightRate.select(*[getattr(AirFreightRate, col) for col in required_columns['air_freight']]).where(AirFreightRate.last_rate_available_date <= DAYS_TO_EXPIRE, AirFreightRate.source != 'predicted')
    
    for rate in ServerSide(fcl_query):
        rate_data = model_to_dict(rate)
        create_air_freight_rate_job(rate_data, 'expiring_rates')
        
    for rate in ServerSide(air_query):
        rate_data = model_to_dict(rate)
        create_fcl_freight_rate_job(rate_data, 'expiring_rates')
