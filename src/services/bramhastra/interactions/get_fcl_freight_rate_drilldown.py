from services.bramhastra.helpers.get_fcl_freight_rate_helper import ClickHouse
from fastapi.encoders import jsonable_encoder
from services.bramhastra.helpers.filter_helper import (
    get_direct_indirect_filters
)


def get_fcl_freight_rate_drilldown(filters):
    where =  get_direct_indirect_filters(filters)
    search_to_book_statistics = get_search_to_book_statistics(filters,where)
    feedback_statistics = get_feedback_statistics(filters,where)
    missing_rates_statistics = get_missing_rates(filters,where)
    stale_rate_statistics = get_stale_rate_statistics(filters,where)
    return dict(
        search_to_book_statistics = search_to_book_statistics,
        feedback_statistics=feedback_statistics,
        missing_rates_statistics = missing_rates_statistics,
        stale_rate_statistics = stale_rate_statistics,
    )
    
    
def get_stale_rate_statistics(filters,where):
    clickhouse = ClickHouse()
    queries = [
        """
        SELECT count(id) FROM brahmastra.fcl_freight_rate_statistics
        """
    ]

    if where:
        queries.append(" AND ")
        queries.append(where)

    charts = jsonable_encoder(clickhouse.execute(" ".join(queries), filters))

    return charts
    
def get_missing_rates(filters,where):
    pass
    
def get_feedback_statistics(filters, where):
    pass


async def get_search_to_book_statistics(filters, where):
    clickhouse = ClickHouse()
    queries = [
        """SELECT 
        SUM(spot_search_count) as spot_search,
        SUM(checkout_count) as checkout,
        FLOOR(AVG(1-checkout_count/spot_search_count),2) AS checkoout_percentage,
        SUM(shipment_confirmed_by_service_provider_count) AS shipment_confirmed_by_service_provider,
        FLOOR(AVG(1-shipment_confirmed_by_service_provider_count/checkout_count),2) AS confirmed_booking_percentage,
        SUM(revenue_desk_visit_count) AS revenue_desk_visit,
        FLOOR(AVG(1-revenue_desk_visit_count/shipment_confirmed_by_service_provider_count),2) AS revenue_desk_visit_percentage,
        SUM(so1_visit_count) AS so1_visit,
        FLOOR(AVG(1-so1_visit_count/revenue_desk_visit_count),2) AS so1_visit_percentage
        FROM brahmastra.fcl_freight_rate_statistics
        """
    ]

    if where:
        queries.append(" WHERE ")
        queries.append(where)

    charts = jsonable_encoder(clickhouse.execute(" ".join(queries), filters))

    return charts