from fastapi.encoders import jsonable_encoder
from datetime import datetime, timedelta
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_jobs import create_fcl_freight_rate_jobs
from services.air_freight_rate.interactions.create_air_freight_rate_jobs import create_air_freight_rate_jobs
from services.bramhastra.models.fcl_freight_rate_statistic import FclFreightRateStatistic
from services.bramhastra.models.air_freight_rate_statistic import AirFreightRateStatistic

SEVEN_DAYS_AGO = datetime.today()-timedelta(7)

def cancelled_shipments_scheduler():
    services = ['fcl_freight', 'air_freight']
    required_columns = {
        'fcl_freight': ['rate_id', 'origin_port_id', 'origin_main_port_id', 'destination_port_id', 'destination_main_port_id',
                        'shipping_line_id', 'service_provider_id', 'container_size', 'container_type', 'commodity', 'rate_type'],
        'air_freight': ['rate_id', 'origin_airport_id','destination_airport_id','commodity', 'airline_id', 'service_provider_id', 'rate_type', 'commodity_type', 'commodity_sub_type', 'operation_type', 'shipment_type', 'stacking_type', 'price_type']
    }

    for service in services:
        if service == "fcl_freight":
            fcl_query = FclFreightRateStatistic.select(*[getattr(FclFreightRateStatistic, col) for col in required_columns['fcl_freight']]).where(
                    (FclFreightRateStatistic.updated_at >= SEVEN_DAYS_AGO),
                    (FclFreightRateStatistic.shipment_cancelled_count > 0)
                )
        if service == "air_freight":
            air_query = AirFreightRateStatistic.select(*[getattr(AirFreightRateStatistic, col) for col in required_columns['air_freight']]).where(
                    (AirFreightRateStatistic.updated_at >= SEVEN_DAYS_AGO),
                    (AirFreightRateStatistic.shipment_cancelled_count > 0)
                )
        
    fcl_data = jsonable_encoder(list(fcl_query.dicts()))
    air_data = jsonable_encoder(list(air_query.dicts()))

    create_fcl_freight_rate_jobs(fcl_data, 'cancelled_shipments')
    create_air_freight_rate_jobs(air_data, 'cancelled_shipments')


