from services.bramhastra.client import ClickHouse
from configs.env import *

LIFETIME = 60

def create_rate_count_dictionary():
    client = ClickHouse().client
    query = f'''
        CREATE DICTIONARY country_rate_count
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
        LIFETIME({LIFETIME})
    '''
    client.execute(query)
    
    
if __name__ == '__main__':   
    create_rate_count_dictionary()