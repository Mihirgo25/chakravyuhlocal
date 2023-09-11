from datetime import datetime, timedelta
from services.air_freight_rate.interactions.create_air_freight_rate_job import create_air_freight_rate_job
from services.bramhastra.models.air_freight_rate_statistic import AirFreightRateStatistic
from playhouse.shortcuts import model_to_dict
from playhouse.postgres_ext import ServerSide


SEVEN_DAYS_AGO = datetime.today().date() - timedelta(days=7)

def air_freight_cancelled_shipments_scheduler():
    required_columns = ['rate_id', 'origin_airport_id','destination_airport_id','commodity', 'airline_id', 'service_provider_id', 'rate_type', 'commodity_type', 'commodity_sub_type', 'operation_type', 'shipment_type', 'stacking_type', 'price_type']

    air_query = AirFreightRateStatistic.select(*[getattr(AirFreightRateStatistic, col) for col in required_columns]).where(
            (AirFreightRateStatistic.updated_at >= SEVEN_DAYS_AGO),
            (AirFreightRateStatistic.shipment_cancelled_count > 0)
        )

    for rate in ServerSide(air_query):
        rate_data = model_to_dict(rate)
        rate_data['id'] = rate_data['rate_id']
        create_air_freight_rate_job(rate_data, 'cancelled_shipments')


