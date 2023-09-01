from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.supply_tool.interactions.create_air_freight_rate_jobs import create_air_freight_rate_jobs
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_jobs import create_fcl_freight_rate_jobs
import datetime
from fastapi.encoders import jsonable_encoder

DAYS_TO_EXPIRE = datetime.datetime.now() + datetime.timedelta(days=7)

def expired_shipments_scheduler():
    services = ['fcl_freight', 'air_freight']

    required_columns = {
        'fcl_freight': ['id', 'origin_port_id', 'origin_port', 'origin_main_port_id', 'destination_port_id', 'destination_port','destination_main_port_id',
                        'shipping_line_id', 'shipping_line', 'service_provider_id', 'service_provider','container_size', 'container_type', 'commodity', 'rate_type','last_rate_available_date'],
        'air_freight': ['id', 'origin_airport_id', 'origin_airport','destination_airport_id', 'destination_airport','commodity', 'airline_id', 'service_provider_id', 'length', 'breadth', 'height']
    }
    
    for service in services:
        if service == "fcl_freight":
            fcl_query = FclFreightRate.select(*[getattr(FclFreightRate, col) for col in required_columns['fcl_freight']]).where(FclFreightRate.last_rate_available_date <= DAYS_TO_EXPIRE)
        if service == 'air_freight':
            air_query = AirFreightRate.select(*[getattr(AirFreightRate, col) for col in required_columns['air_freight']]).where(AirFreightRate.last_rate_available_date <= DAYS_TO_EXPIRE)
    
    fcl_data = jsonable_encoder(list(fcl_query.dicts()))
    air_data = jsonable_encoder(list(air_query.dicts()))

    for item in fcl_data:
        item['rate_id'] = item.pop('id')
    for item in air_data:
        item['rate_id'] = item.pop('id')

    create_fcl_freight_rate_jobs(fcl_data, 'expiring_rates')
    create_air_freight_rate_jobs(air_data, 'expiring_rates')