from services.bramhastra.client import ClickHouse
from fastapi.encoders import jsonable_encoder
from micro_services.client import maps
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)


async def get_fcl_freight_rate_world():
    statistics = await get_past_count()

    count = await get_total_count()

    return {
        "total_rates": count,
        "statistics": statistics,
    }


async def get_total_count():
    query = "SELECT count(id) as count FROM brahmastra.fcl_freight_rate_statistics"
    clickhouse = ClickHouse()
    if result := clickhouse.execute(query):
        return result[0]["count"]


async def get_past_count():
    clickhouse = ClickHouse()

    query = f"""
            WITH clean_rates AS
            (
                SELECT
                    origin_country_id,
                    destination_country_id,
                    id,
                    sum(sign)
                FROM brahmastra.{FclFreightRateStatistic._meta.table_name}
                GROUP BY
                    id,
                    origin_country_id,
                    destination_country_id
                HAVING sum(sign) > 0
                ORDER BY id ASC
            )
        SELECT
            country_id,
            dictGet('brahmastra.country_rate_count', 'rate_count', country_id) + COUNT(*) AS rate_count
        FROM
        (
            SELECT origin_country_id AS country_id
            FROM clean_rates
            UNION ALL
            SELECT destination_country_id AS country_id
            FROM clean_rates
        ) AS combined_countries
        GROUP BY country_id"""

    return jsonable_encoder(clickhouse.execute(query))
