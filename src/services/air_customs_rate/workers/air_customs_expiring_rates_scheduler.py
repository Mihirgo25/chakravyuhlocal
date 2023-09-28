from services.air_customs_rate.models.air_customs_rate import AirCustomsRate
from services.air_customs_rate.interaction.create_air_customs_rate_job import (
    create_air_customs_rate_job,
)
import datetime
from playhouse.postgres_ext import ServerSide
from playhouse.shortcuts import model_to_dict
from configs.global_constants import DEFAULT_SERVICE_PROVIDER_ID


DAYS_TO_EXPIRE = datetime.datetime.now().date() + datetime.timedelta(days=2)


def air_customs_expiring_rates_scheduler():

    required_columns = [
        "id",
        "airport_id",
        "airport",
        "commodity",
        "service_provider_id",
        "rate_type",
        "commodity_type",
        "commodity_sub_type",
        "operation_type",
        "shipment_type",
        "stacking_type",
        "price_type",
        "last_rate_available_date"
    ]

    air_query = AirCustomsRate.select(
        *[getattr(AirCustomsRate, col) for col in required_columns]
    ).where(

        AirCustomsRate.last_rate_available_date == DAYS_TO_EXPIRE,
        AirCustomsRate.mode.not_in(["predicted", "cluster_extension"]),
        AirCustomsRate.rate_type == "market_place",
        AirCustomsRate.service_provider_id != DEFAULT_SERVICE_PROVIDER_ID,
    )

    for rate in ServerSide(air_query):
        rate_data = model_to_dict(rate)
        create_air_customs_rate_job(rate_data, "expiring_rates")