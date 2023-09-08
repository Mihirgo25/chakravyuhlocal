from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.interactions.create_air_freight_rate_job import (
    create_air_freight_rate_job,
)
import datetime
from playhouse.postgres_ext import ServerSide
from playhouse.shortcuts import model_to_dict
from services.air_freight_rate.models.air_freight_location_cluster import (
    AirFreightLocationCluster,
)
from fastapi.encoders import jsonable_encoder
from services.air_freight_rate.constants.air_freight_rate_constants import (
    CRITICAL_AIRPORTS_INDIA_VIETNAM,
)
from services.air_freight_rate.constants.air_freight_rate_constants import COGOXPRESS

DAYS_TO_EXPIRE = datetime.datetime.now().date() + datetime.timedelta(days=2)


def air_freight_expiring_rates_scheduler():
    required_columns = [
        "id",
        "origin_airport_id",
        "origin_airport",
        "destination_airport_id",
        "destination_airport",
        "commodity",
        "airline_id",
        "service_provider_id",
        "rate_type",
        "commodity_type",
        "commodity_sub_type",
        "operation_type",
        "shipment_type",
        "stacking_type",
        "price_type",
    ]

    all_air_critical_ports = AirFreightLocationCluster.select(
        AirFreightLocationCluster.base_airport_id
    )
    all_air_critical_ports = jsonable_encoder(list(all_air_critical_ports.dicts()))
    air_critical_ports_except_in_vn = [
        str(i["base_airport_id"])
        for i in all_air_critical_ports
        if str(i["base_airport_id"]) not in CRITICAL_AIRPORTS_INDIA_VIETNAM
    ]

    air_query = AirFreightRate.select(
        *[getattr(AirFreightRate, col) for col in required_columns]
    ).where(
        (
            (AirFreightRate.origin_airport_id << CRITICAL_AIRPORTS_INDIA_VIETNAM)
            & (AirFreightRate.destination_airport_id << air_critical_ports_except_in_vn)
        )
        | (
            (AirFreightRate.origin_airport_id << air_critical_ports_except_in_vn)
            & (AirFreightRate.destination_airport_id << CRITICAL_AIRPORTS_INDIA_VIETNAM)
        ),
        AirFreightRate.last_rate_available_date == DAYS_TO_EXPIRE,
        ~(AirFreightRate.rate_not_available_entry),
        AirFreightRate.source.not_in(["predicted", "rate_extention"]),
        AirFreightRate.rate_type == "market_place",
        AirFreightRate.service_provider_id != COGOXPRESS,
    )

    for rate in ServerSide(air_query):
        rate_data = model_to_dict(rate)
        create_air_freight_rate_job(rate_data, "expiring_rates")
