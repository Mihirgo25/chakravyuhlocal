from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.interactions.create_air_freight_rate_job import (
    create_air_freight_rate_job,
)
from services.air_freight_rate.constants.air_freight_rate_constants import (
     INDIA_CRITICAL_PORT_PAIR, VIETNAM_CRITICAL_PORT_PAIRS
)
import datetime
from playhouse.postgres_ext import ServerSide
from playhouse.shortcuts import model_to_dict

SEVEN_DAYS_AGO = datetime.datetime.now().date() - datetime.timedelta(days=7)
TODAYS_DATE = datetime.datetime.now().date()
from services.air_freight_rate.constants.air_freight_rate_constants import COGOXPRESS



REQUIRED_COLUMNS = [
    "id",
    "origin_airport_id",
    "origin_airport",
    "destination_airport_id",
    "destination_airport",
    "commodity",
    "airline_id",
    "service_provider_id",
    "commodity_type",
    "commodity_sub_type",
    "operation_type",
    "shipment_type",
    "stacking_type",
    "price_type",
]


def air_freight_critical_port_pairs_scheduler():

    air_query = AirFreightRate.select(
        *[getattr(AirFreightRate, col) for col in REQUIRED_COLUMNS]
    ).where(
        (AirFreightRate.updated_at.cast("date") == SEVEN_DAYS_AGO),
        AirFreightRate.source.not_in(["predicted", "cluster_extension"]),
        AirFreightRate.rate_type == "market_place",
        AirFreightRate.service_provider_id != COGOXPRESS,
    )
    condition = None

    for pairs in INDIA_CRITICAL_PORT_PAIR:
        current_condition = (
            (AirFreightRate.origin_airport_id == pairs['origin_airport_id']) |
            (AirFreightRate.destination_airport_id == pairs['destination_airport_id'])
        )
        
        if condition is None:
            condition = current_condition
        else:
            condition = condition | current_condition

    for pairs in VIETNAM_CRITICAL_PORT_PAIRS:
        current_condition = (
            (AirFreightRate.origin_airport_id == pairs['origin_airport_id']) |
            (AirFreightRate.destination_airport_id == pairs['destination_airport_id'])
        )
        
        if condition is None:
            condition = current_condition
        else:
            condition = condition | current_condition

    air_query = air_query.where(condition)
   
    for rate in ServerSide(air_query):
        rate_data = model_to_dict(rate)
        create_air_freight_rate_job(rate_data, "critical_ports")
