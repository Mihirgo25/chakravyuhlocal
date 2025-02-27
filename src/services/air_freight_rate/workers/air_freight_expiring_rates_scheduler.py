from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.interactions.create_air_freight_rate_job import (
    create_air_freight_rate_job,
)
import datetime, json, os
from playhouse.postgres_ext import ServerSide
from playhouse.shortcuts import model_to_dict
from services.air_freight_rate.constants.air_freight_rate_constants import COGOXPRESS
from configs.definitions import ROOT_DIR

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

    air_query = AirFreightRate.select(
        *[getattr(AirFreightRate, col) for col in required_columns]
    ).where(
        AirFreightRate.last_rate_available_date == DAYS_TO_EXPIRE,
        ~(AirFreightRate.rate_not_available_entry),
        AirFreightRate.source.not_in(["predicted", "rate_extention"]),
        AirFreightRate.rate_type == "market_place",
        AirFreightRate.service_provider_id != COGOXPRESS,
        AirFreightRate.commodity == "general",
    )
    condition = None

    critical_port_pairs_india_path = os.path.join(
        ROOT_DIR, "libs", "air_freight_critical_port_pairs_india.json"
    )
    with open(critical_port_pairs_india_path, "r") as json_file:
        india_critical_port_pairs = json.load(json_file)

        for pairs in india_critical_port_pairs:
            current_condition = (
                AirFreightRate.origin_airport_id == pairs["origin_airport_id"]
            ) | (
                AirFreightRate.destination_airport_id == pairs["destination_airport_id"]
            )

            if condition is None:
                condition = current_condition
            else:
                condition = condition | current_condition

    critical_port_pairs_vietnam_path = os.path.join(
        ROOT_DIR, "libs", "air_freight_critical_port_pairs_vietnam.json"
    )
    with open(critical_port_pairs_vietnam_path, "r") as json_file:
        vietnam_critical_port_pairs = json.load(json_file)

        for pairs in vietnam_critical_port_pairs:
            current_condition = (
                AirFreightRate.origin_airport_id == pairs["origin_airport_id"]
            ) | (
                AirFreightRate.destination_airport_id == pairs["destination_airport_id"]
            )

            if condition is None:
                condition = current_condition
            else:
                condition = condition | current_condition
    if condition:
        air_query = air_query.where(condition)

    for rate in ServerSide(air_query):
        rate_data = model_to_dict(rate)
        create_air_freight_rate_job(rate_data, "expiring_rates")
