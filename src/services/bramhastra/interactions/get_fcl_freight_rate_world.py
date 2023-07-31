from services.bramhastra.clickhouse.client import ClickHouse
from fastapi.encoders import jsonable_encoder
from micro_services.client import maps
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from peewee import fn
from collections import defaultdict


async def get_fcl_freight_rate_world():
    past_statistics = await get_past_count()
    live_statistics = await get_live_count()

    merge(past_statistics, live_statistics)

    add_location_objects(live_statistics)

    total_rates = 0

    for statistic in live_statistics:
        total_rates += statistic["rate_count"]

    return {"total_rates": total_rates, "statistics": live_statistics}


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


async def get_past_count():
    clickhouse = ClickHouse()

    query = """SELECT country_id,COUNT(*) AS rate_count FROM 
    (SELECT origin_country_id AS country_id
    FROM brahmastra.fcl_freight_rate_statistics
    UNION ALL
    SELECT destination_country_id AS country_id
    FROM brahmastra.fcl_freight_rate_statistics) AS combined_countries
    GROUP BY country_id"""

    return jsonable_encoder(clickhouse.execute(query))


async def get_live_count():
    subquery = (
        FclFreightRateStatistic.select(
            FclFreightRateStatistic.origin_country_id.alias("country_id")
        )
        .union_all(
            FclFreightRateStatistic.select(
                FclFreightRateStatistic.destination_country_id.alias("country_id")
            )
        )
        .alias("combined_countries")
    )

    return jsonable_encoder(
        list(
            FclFreightRateStatistic.select(
                subquery.c.country_id,
                fn.COUNT(subquery.c.country_id).alias("rate_count"),
            )
            .from_(subquery)
            .group_by(subquery.c.country_id)
            .dicts()
        )
    )


def merge(past_statistics, live_statistics):
    merged_dict = defaultdict(int)

    for item in past_statistics:
        merged_dict[item['country_id']] += item['rate_count']

    for item in live_statistics:
        merged_dict[item['country_id']] += item['rate_count']

    return [{'country_id': k, 'rate_count': v} for k, v in merged_dict.items()]
