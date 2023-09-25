from datetime import datetime, timedelta
from services.haulage_freight_rate.interactions.create_haulage_freight_rate_job import create_haulage_freight_rate_job
from services.bramhastra.models.haulage_freight_rate_statistic import HaulageFreightRateStatistic
from playhouse.shortcuts import model_to_dict
from playhouse.postgres_ext import ServerSide


SEVEN_DAYS_AGO = datetime.today().date() - timedelta(days=7)

def haulage_freight_cancelled_shipments_scheduler():
    required_columns = ['rate_id', 'origin_location_id', 'origin_location', 'destination_location_id', 'destination_location',
                        'shipping_line_id', 'service_provider_id', 'container_size', 'container_type', 'commodity', 'rate_type']


    haulage_query = HaulageFreightRateStatistic.select(*[getattr(HaulageFreightRateStatistic, col) for col in required_columns]).where(
            (HaulageFreightRateStatistic.updated_at >= SEVEN_DAYS_AGO),
            (HaulageFreightRateStatistic.shipment_cancelled_count > 0)
        )

    for rate in ServerSide(haulage_query):
        rate_data = model_to_dict(rate)
        create_haulage_freight_rate_job(rate_data, 'cancelled_shipments')