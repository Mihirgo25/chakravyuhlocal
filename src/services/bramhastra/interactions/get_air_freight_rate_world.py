from services.bramhastra.client import ClickHouse
from fastapi.encoders import jsonable_encoder
from services.bramhastra.models.air_freight_rate_statistic import (
    AirFreightRateStatistic,
)


def get_air_freight_rate_world():
    statistics = get_count_distribution()

    count = get_total_count()

    return {
        "total_rates": count,
        "statistics": statistics,
    }


def get_total_count():
    query = f"SELECT COUNT(DISTINCT rate_id) as count FROM brahmastra.{AirFreightRateStatistic._meta.table_name} WHERE validity_end >= toDate(now())"
    clickhouse = ClickHouse()
    if result := clickhouse.execute(query):
        return result[0]["count"]


def get_count_distribution():
    clickhouse = ClickHouse()

    query = f"""
            WITH clean_rates AS
            (
                SELECT
                    origin_country_id,
                    destination_country_id,
                    rate_id
                FROM brahmastra.{AirFreightRateStatistic._meta.table_name} WHERE validity_end >= toDate(now())
                GROUP BY
                    rate_id,
                    origin_country_id,
                    destination_country_id
            )
        SELECT
            country_id,
            COUNT(*) AS rate_count
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
