from services.bramhastra.client import ClickHouse
from fastapi.encoders import jsonable_encoder
from micro_services.client import maps
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from peewee import fn
from collections import defaultdict


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

    query = """
    WITH clean_rates AS (
        SELECT origin_country_id,destination_country_id,sum(sign) from brahmastra.fcl_freight_rate_statistics
        GROUP BY origin_country_id,destination_country_id HAVING sum(sign) > 0 ORDER BY id ASC
    )
    SELECT country_id, dictGet('country_rate_count', 'rate_count', country_id) + COUNT(*) AS rate_count FROM 
    (SELECT origin_country_id AS country_id
    FROM clean_rates
    UNION ALL
    SELECT destination_country_id AS country_id
    FROM clean_rates) AS combined_countries
    GROUP BY country_id"""

    return jsonable_encoder(clickhouse.execute(query))


