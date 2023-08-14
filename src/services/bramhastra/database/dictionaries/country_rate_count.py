from services.bramhastra.client import ClickHouse
from configs.env import (
    DATABASE_NAME,
    DATABASE_HOST,
    DATABASE_PASSWORD,
    DATABASE_USER,
    DATABASE_PORT,
)


class CountryRateCount:
    def __init__(self) -> None:
        self.lifetime = 60
        self.client = ClickHouse().client

        self.query = f"""
            CREATE DICTIONARY brahmastra.country_rate_count
            (
                country_id UUID,
                rate_count UInt64
            )
            PRIMARY KEY country_id 
            SOURCE(POSTGRESQL(
                port {DATABASE_PORT}
                host {DATABASE_HOST}
                user {DATABASE_USER}
                password {DATABASE_PASSWORD}
                db {DATABASE_NAME}                                                                                                                                                                                              
                replica(host {DATABASE_HOST} port {DATABASE_PORT} priority 1)
                query 'SELECT "combined_countries"."country_id", COUNT("combined_countries"."country_id") AS "rate_count" FROM ((SELECT "t1"."origin_country_id" AS "country_id" FROM "fcl_freight_rate_statistics" AS "t1") UNION ALL (SELECT "t2"."destination_country_id" AS "country_id" FROM "fcl_freight_rate_statistics" AS "t2")) AS "combined_countries" GROUP BY "combined_countries"."country_id"'
            ))
            LAYOUT(COMPLEX_KEY_HASHED_ARRAY())
            LIFETIME({self.lifetime})
        """
        
    def create(self):
        self.client.execute(self.query)
