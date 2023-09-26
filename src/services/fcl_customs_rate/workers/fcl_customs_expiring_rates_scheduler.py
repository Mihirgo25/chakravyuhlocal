from services.fcl_customs_rate.models.fcl_customs_rate import FclCustomsRate
from services.fcl_customs_rate.interaction.create_fcl_customs_rate_job import (
    create_fcl_customs_rate_job,
)
import datetime
from playhouse.postgres_ext import ServerSide
from playhouse.shortcuts import model_to_dict
from configs.global_constants import DEFAULT_SERVICE_PROVIDER_ID


DAYS_TO_EXPIRE = datetime.datetime.now().date() + datetime.timedelta(days=2)


def fcl_customs_expiring_rates_scheduler():

    required_columns = [
        "id",
        "location_id",
        "location",
        "service_provider_id",
        "service_provider",
        "container_size",
        "container_type",
        "commodity",
        "rate_type",
        "last_rate_available_date",
    ]

    fcl_query = FclCustomsRate.select(
        *[getattr(FclCustomsRate, col) for col in required_columns]
    ).where(

        FclCustomsRate.last_rate_available_date == DAYS_TO_EXPIRE,
        FclCustomsRate.mode.not_in(["predicted", "cluster_extension"]),
        FclCustomsRate.rate_type == "market_place",
        FclCustomsRate.service_provider_id != DEFAULT_SERVICE_PROVIDER_ID,
    )

    for rate in ServerSide(fcl_query):
        rate_data = model_to_dict(rate)
        create_fcl_customs_rate_job(rate_data, "expiring_rates")