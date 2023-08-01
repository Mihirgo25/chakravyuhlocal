from services.bramhastra.clickhouse.client import ClickHouse
from fastapi.encoders import jsonable_encoder
from micro_services.client import maps
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from peewee import fn
from collections import defaultdict
import time


def get_fcl_freight_rate_world():
    statistics = get_past_count()  
    
    return {"total_rates": sum(statistic["rate_count"] for statistic in statistics), "statistics": statistics}


def add_location_objects(statistics):
    location_ids = [statistic["country_id"] for statistic in statistics]

    if not location_ids:
        return

    locations = {
        location["id"]: location
        for location in maps.list_locations(
            dict(
                filters=dict(id=location_ids),
                includes=dict(id=True, name=True),
                page_limit=len(location_ids),
            )
        )["list"]
    }

    for statistic in statistics:
        statistic["country_name"] = locations[statistic["country_id"]]["name"]


def get_past_count():
    clickhouse = ClickHouse()

    query = """SELECT country_id, dictGet('country_rate_count', 'rate_count', country_id) + SUM(sign)/2 AS rate_count FROM 
    (SELECT sign, origin_country_id AS country_id
    FROM brahmastra.fcl_freight_rate_statistics
    UNION ALL
    SELECT sign, destination_country_id AS country_id
    FROM brahmastra.fcl_freight_rate_statistics) AS combined_countries
    GROUP BY country_id"""

    return jsonable_encoder(clickhouse.execute(query))


