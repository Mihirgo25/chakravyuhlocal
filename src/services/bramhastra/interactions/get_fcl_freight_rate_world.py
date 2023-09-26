from services.bramhastra.client import ClickHouse
from fastapi.encoders import jsonable_encoder
from micro_services.client import maps
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)

FILTER_MAPPING = {
    "import":"origin",
    "export": "destination"
}
async def get_fcl_freight_rate_world(filters):

    statistics = await get_count_distribution(filters)
    count = await get_total_count()
    return {
        "total_rates": count,
        "statistics": statistics,
    }

async def get_total_count():
    query = "SELECT COUNT(DISTINCT rate_id) as count FROM brahmastra.fcl_freight_rate_statistics WHERE validity_end >= toDate(now())"
    clickhouse = ClickHouse()
    if result := clickhouse.execute(query):
        return result[0]["count"]


async def get_count_distribution(filters):
    trade = "origin"
    location = "country"
    if "trade_type" in filters:
        trade = FILTER_MAPPING[filters["trade_type"]]
    
    if "location_type" in filters:
        location = filters["location_type"]    
    
    clickhouse = ClickHouse()

    query = f"""
            WITH clean_rates AS
            (
                SELECT
                    {trade}_{location}_id,
                    rate_id
                FROM brahmastra.{FclFreightRateStatistic._meta.table_name} WHERE validity_end >= toDate(now())
                GROUP BY
                    {trade}_{location}_id,
                    rate_id
            )
        SELECT
            {location}_id,
            COUNT(*) AS rate_count
        FROM
        (
            SELECT {trade}_{location}_id AS {location}_id
            FROM clean_rates
        ) AS combined_countries
        GROUP BY {location}_id"""

    return jsonable_encoder(clickhouse.execute(query))