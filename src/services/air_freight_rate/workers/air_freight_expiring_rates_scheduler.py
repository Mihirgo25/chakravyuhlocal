from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.interactions.create_air_freight_rate_job import create_air_freight_rate_job
import datetime
from playhouse.postgres_ext import ServerSide
from playhouse.shortcuts import model_to_dict

DAYS_TO_EXPIRE = datetime.datetime.now().date() + datetime.timedelta(days=7)

def air_freight_expiring_rates_scheduler():

    required_columns = ['id', 'origin_airport_id', 'origin_airport','destination_airport_id', 'destination_airport','commodity', 'airline_id', 'service_provider_id', 'rate_type', 'commodity_type', 'commodity_sub_type', 'operation_type', 'shipment_type', 'stacking_type', 'price_type']
    
    air_query = AirFreightRate.select(*[getattr(AirFreightRate, col) for col in required_columns]).where(AirFreightRate.last_rate_available_date <= DAYS_TO_EXPIRE, AirFreightRate.source != 'predicted')
    for rate in ServerSide(air_query):
        rate_data = model_to_dict(rate)
        create_air_freight_rate_job(rate_data, 'expiring_rates')
