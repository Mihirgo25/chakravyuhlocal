from services.bramhastra.client import ClickHouse
from services.bramhastra.helpers.air_freight_filter_helper import get_direct_indirect_filters


def get_air_freight_rate_distribution(filters):
    clickhouse = ClickHouse()

    queries = [
        """WITH rate_distribution as 
               (SELECT source,shipment_cancelled_count,shipment_completed_count,shipment_confirmed_by_service_provider_count,bookings_created,
               shipment_aborted_count,shipment_received_count,shipment_in_progress_count
               from brahmastra.air_freight_rate_statistics"""
    ]

    if where := get_direct_indirect_filters(filters):
        queries.append(" WHERE ")
        queries.append(where)

    queries.append(
        """), source_count AS (
        SELECT
            source,
            COUNT(source) AS value,
            SUM(bookings_created) AS bookings_created,
            SUM(shipment_cancelled_count + shipment_aborted_count) AS shipment_cancelled_count,
            CASE WHEN bookings_created = 0 THEN 0
                ELSE FLOOR((shipment_cancelled_count / NULLIF(bookings_created, 0)) * 100, 2)
            END AS shipment_cancelled_percentage,
            SUM(shipment_completed_count) AS shipment_completed_count,
            CASE WHEN bookings_created = 0 THEN 0
                ELSE FLOOR((shipment_completed_count / NULLIF(bookings_created, 0)) * 100, 2)
            END AS shipment_completed_percentage,
            SUM(shipment_in_progress_count) AS shipment_in_progress_count,
            CASE WHEN bookings_created = 0 THEN 0
                ELSE FLOOR((shipment_in_progress_count / NULLIF(bookings_created, 0)) * 100, 2)
            END AS shipment_in_progress_percentage,
            SUM(shipment_confirmed_by_service_provider_count) AS shipment_confirmed_by_service_provider_count,
            CASE WHEN bookings_created = 0 THEN 0
                ELSE FLOOR((shipment_confirmed_by_service_provider_count / NULLIF(bookings_created, 0)) * 100, 2)
            END AS shipment_confirmed_by_service_provider_percentage,
            SUM(shipment_received_count) AS shipment_received_count,
            CASE WHEN bookings_created = 0 THEN 0
                ELSE FLOOR((shipment_received_count / NULLIF(bookings_created, 0)) * 100, 2)
            END AS shipment_received_percentage
        FROM rate_distribution
        GROUP BY source
    )
    SELECT * FROM source_count"""
    )
    
    response = clickhouse.execute(" ".join(queries), filters)
    
    return format_distribution(response)

def format_distribution(response):
    distribution  = dict()
    total_rates = 0
    for data in response:
        total_rates+=data['value']
        distribution[data['source']] = data
        del data['source']
    distribution['total_rates'] = total_rates
    return distribution
    