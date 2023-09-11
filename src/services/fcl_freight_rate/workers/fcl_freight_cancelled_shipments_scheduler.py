from datetime import datetime, timedelta
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_job import create_fcl_freight_rate_job
from services.bramhastra.models.fcl_freight_rate_statistic import FclFreightRateStatistic
from playhouse.shortcuts import model_to_dict
from playhouse.postgres_ext import ServerSide


SEVEN_DAYS_AGO = datetime.today().date() - timedelta(days=7)

def fcl_freight_cancelled_shipments_scheduler():
    required_columns = ['rate_id', 'origin_port_id', 'origin_main_port_id', 'destination_port_id', 'destination_main_port_id',
                        'shipping_line_id', 'service_provider_id', 'container_size', 'container_type', 'commodity', 'rate_type']


    fcl_query = FclFreightRateStatistic.select(*[getattr(FclFreightRateStatistic, col) for col in required_columns]).where(
            (FclFreightRateStatistic.updated_at >= SEVEN_DAYS_AGO),
            (FclFreightRateStatistic.shipment_cancelled_count > 0)
        )
                
    for rate in ServerSide(fcl_query):
        rate_data = model_to_dict(rate)
        create_fcl_freight_rate_job(rate_data, 'cancelled_shipments')

