from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
from services.haulage_freight_rate.interactions.create_haulage_freight_rate_job import (
    create_haulage_freight_rate_job,
)
import datetime
from playhouse.postgres_ext import ServerSide
from playhouse.shortcuts import model_to_dict
from configs.global_constants import DEFAULT_SERVICE_PROVIDER_ID


DAYS_TO_EXPIRE = datetime.datetime.now().date() + datetime.timedelta(days=2)


def haulage_freight_expiring_rates_scheduler():

    required_columns = [
        "id",
        "origin_location_id",
        "origin_location",
        "destination_location_id",
        "destination_location",
        "shipping_line_id",
        "shipping_line",
        "service_provider_id",
        "service_provider",
        "container_size",
        "container_type",
        "commodity",
        "rate_type",
        "validity_end",
        "haulage_type",
        "trailer_type",
        "trip_type",
        "transport_modes_keyword",
    ]

    haulage_query = HaulageFreightRate.select(
        *[getattr(HaulageFreightRate, col) for col in required_columns]
    ).where(
        HaulageFreightRate.validity_end == DAYS_TO_EXPIRE,
        HaulageFreightRate.source.not_in(["predicted", "cluster_extension"]),
        HaulageFreightRate.rate_type == "market_place",
        HaulageFreightRate.service_provider_id != DEFAULT_SERVICE_PROVIDER_ID,
    )

    for rate in ServerSide(haulage_query):
        rate_data = model_to_dict(rate)
        create_haulage_freight_rate_job(rate_data, "expiring_rates")