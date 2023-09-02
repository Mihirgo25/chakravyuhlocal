from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.interactions.create_air_freight_rate_jobs import create_air_freight_rate_jobs
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_jobs import create_fcl_freight_rate_jobs
from configs.fcl_freight_rate_constants import CRITICAL_PORTS_INDIA_VIETNAM, CRITICAL_AIRPORTS_INDIA_VIETNAM
import datetime
from playhouse.postgres_ext import ServerSide
from playhouse.shortcuts import model_to_dict


SEVEN_DAYS_AGO = datetime.datetime.now() - datetime.timedelta(days=7)

REQUIRED_COLUMNS = {
        'fcl_freight': ['id', 'origin_port_id', 'origin_port', 'origin_main_port_id', 'destination_port_id', 'destination_port','destination_main_port_id',
                        'shipping_line_id', 'shipping_line', 'service_provider_id', 'service_provider','container_size', 'container_type', 'commodity', 'rate_type'],
        'air_freight': ['id', 'origin_airport_id', 'origin_airport','destination_airport_id', 'destination_airport','commodity', 'airline_id', 'service_provider_id', 'commodity_type', 'commodity_sub_type', 'operation_type', 'shipment_type', 'stacking_type', 'price_type']
    }
    

def critical_port_pairs_scheduler():
    services = ['fcl_freight', 'air_freight']

    for service in services:
        if service == "fcl_freight":
            fcl_query = FclFreightRate.select(*[getattr(FclFreightRate, col) for col in REQUIRED_COLUMNS['fcl_freight']]).where(
                    ((FclFreightRate.origin_port_id << CRITICAL_PORTS_INDIA_VIETNAM) |
                    (FclFreightRate.destination_port_id << CRITICAL_PORTS_INDIA_VIETNAM)),
                    (FclFreightRate.updated_at < SEVEN_DAYS_AGO)
                )
        if service == 'air_freight':
            air_query = AirFreightRate.select(*[getattr(AirFreightRate, col) for col in REQUIRED_COLUMNS['air_freight']]).where(
                    ((AirFreightRate.origin_airport_id << CRITICAL_AIRPORTS_INDIA_VIETNAM) |
                    (AirFreightRate.destination_airport_id << CRITICAL_AIRPORTS_INDIA_VIETNAM)),
                    (AirFreightRate.updated_at < SEVEN_DAYS_AGO)
                )
            
    for rate in ServerSide(fcl_query):
        rate_data = model_to_dict(rate)
        create_fcl_freight_rate_jobs(rate_data, 'critical_ports')
        
    for rate in ServerSide(air_query):
        rate_data = model_to_dict(rate)
        create_air_freight_rate_jobs(rate_data, 'critical_ports')
