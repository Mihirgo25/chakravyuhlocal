from services.bramhastra.helpers.clickhouse_helper import ClickHouse
from fastapi.encoders import jsonable_encoder
from micro_services.client import maps


def get_fcl_freight_rate_world():
    clickhouse = ClickHouse()

    query = """SELECT country_id,COUNT(*) AS rate_count FROM 
    (SELECT origin_country_id AS country_id
    FROM brahmastra.fcl_freight_rate_statistics
    UNION ALL
    SELECT destination_country_id AS country_id
    FROM brahmastra.fcl_freight_rate_statistics) AS combined_countries
    GROUP BY country_id"""

    statistics = jsonable_encoder(clickhouse.execute(query))

    add_location_objects(statistics)

    total_rates = 0

    for statistic in statistics:
        total_rates += statistic["rate_count"]

    return {"total_rates": total_rates, "statistics": statistics}


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
