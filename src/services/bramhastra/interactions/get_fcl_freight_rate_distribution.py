from services.bramhastra.clickhouse.client import Clickhouse
from services.bramhastra.helpers.fcl_freight_filter_helper import get_direct_indirect_filters


def get_fcl_freight_rate_distribution(filters):
    clickhouse = ClickHouse()

    queries = [
        """WITH rate_distribution as 
               (SELECT mode,shipment_cancelled_count,shipment_completed_count,shipment_confirmed_by_service_provider_count,bookings_created,
               shipment_aborted_count,shipment_recieved_count,shipment_in_progress_count
               from brahmastra.fcl_freight_rate_statistics"""
    ]

    if where := get_direct_indirect_filters(filters):
        queries.append(" WHERE ")
        queries.append(where)

    queries.append(
        """), mode_count as (SELECT mode,count(mode) as value,
        sum(bookings_created) as bookings_created,
        sum(shipment_cancelled_count + shipment_aborted_count) as shipment_cancelled_count,
        floor((shipment_cancelled_count/bookings_created)*100,2) as shipment_cancelled_percentage,
        sum(shipment_completed_count) as shipment_completed_count,
        floor((shipment_completed_count/bookings_created)*100,2) as shipment_completed_percentage,
        sum(shipment_in_progress_count)  as shipment_in_progress_count,
        floor((shipment_in_progress_count/bookings_created)*100,2) as shipment_in_progress_percentage,
        sum(shipment_confirmed_by_service_provider_count)  as shipment_confirmed_by_service_provider_count, 
        floor((shipment_confirmed_by_service_provider_count/bookings_created)*100,2) as shipment_confirmed_by_service_provider_percentage,  
        sum(shipment_recieved_count)  as shipment_recieved_count,
        floor((shipment_recieved_count/bookings_created)*100,2) as shipment_recieved_percentage
        from rate_distribution group by mode)
           SELECT * from mode_count"""
    )
    
    response = clickhouse.execute(" ".join(queries), filters)
    
    return format_distribution(response)

def format_distribution(response):
    distribution  = dict()
    total_rates = 0
    for data in response:
        total_rates+=data['value']
        distribution[data['mode']] = data
        del data['mode']
    distribution['total_rates'] = total_rates
    return distribution
    