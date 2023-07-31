from services.bramhastra.helpers.clickhouse_helper import ClickHouse
from services.bramhastra.helpers.air_freight_filter_helper import get_direct_indirect_filters


def get_air_freight_rate_distribution(filters):
    clickhouse = ClickHouse()

    queries = [
        """WITH rate_distribution as 
               (SELECT source,shipment_cancelled_count,shipment_completed_count,shipment_confirmed_by_service_provider_count,bookings_created,
               shipment_aborted_count
               from brahmastra.air_freight_rate_statistics"""
    ]

    if where := get_direct_indirect_filters(filters):
        queries.append(" WHERE ")
        queries.append(where)

    queries.append(
        """), source_count as (SELECT source,count(source) as value,
        sum(bookings_created) as bookings_created,
        sum(shipment_cancelled_count + shipment_aborted_count) as shipment_cancelled_count,
        floor((shipment_cancelled_count/bookings_created)*100,2) as shipment_cancelled_percentage,
        sum(shipment_completed_count) as shipment_completed_count,
        floor((shipment_completed_count/bookings_created)*100,2) as shipment_completed_percentage,
        sum(shipment_confirmed_by_service_provider_count)  as shipment_confirmed_by_service_provider_count, 
        floor((shipment_confirmed_by_service_provider_count/bookings_created)*100,2) as shipment_confirmed_by_service_provider_percentage
        from rate_distribution group by source)
           SELECT * from source_count"""
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
    