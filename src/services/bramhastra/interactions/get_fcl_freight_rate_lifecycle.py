from services.bramhastra.helpers.get_fcl_freight_rate_helper import ClickHouse
from fastapi.encoders import jsonable_encoder
from services.bramhastra.helpers.filter_helper import get_direct_indirect_filters


async def get_fcl_freight_rate_lifecycle(filters):
    where = get_direct_indirect_filters(filters)
    search_to_book_statistics = await get_search_to_book_and_feedback_statistics(
        filters.copy(), where
    )

    missing_rates_statistics = await get_missing_rates(filters.copy(), where)

    stale_rate_statistics = await get_stale_rate_statistics(filters.copy(), where)

    statistics = [
        [
            {
                "action_type": "checkout",
                "rates_count": search_to_book_statistics["checkout"],
                "drop": search_to_book_statistics["checkoout_percentage"],
            },
            {
                "action_type": "booking_confirm",
                "rates_count": search_to_book_statistics[
                    "shipment_confirmed_by_service_provider"
                ],
                "drop": search_to_book_statistics["confirmed_booking_percentage"],
            },
            {
                "action_type": "revenue_desk",
                "rates_count": search_to_book_statistics["revenue_desk_visit"],
                "drop": search_to_book_statistics["revenue_desk_visit_percentage"],
            },
            {
                "action_type": "so1",
                "rates_count": search_to_book_statistics["so1_visit"],
                "drop": search_to_book_statistics["so1_visit_percentage"],
            },
        ],
        [
            {"action_type": "missing_rates", "rates_count": 4323, "drop": 71},
            {"action_type": "rates_triggered", "rates_count": 1200, "drop": 71},
            {"action_type": "rates_updated", "rates_count": 540, "drop": 71},
        ],
        [
            {
                "action_type": "disliked_rates",
                "rates_count": search_to_book_statistics["dislikes"],
                "drop": search_to_book_statistics["dislikes_percentage"],
            },
            {
                "action_type": "feedback_received",
                "rates_count": search_to_book_statistics["feedback_recieved"],
                "drop": search_to_book_statistics["feedback_recieved_percentage"],
            },
            {
                "action_type": "rates_reverted",
                "rates_count": search_to_book_statistics["dislikes_rate_reverted"],
                "drop": search_to_book_statistics["dislikes_rate_reverted_percentage"],
            },
        ],
        [
            {
                "action_type": "stale_rates",
                "rates_count": stale_rate_statistics[0]["stale_rates"],
            },
        ],
    ]

    return dict(searches=search_to_book_statistics["spot_search"], cards=statistics)


async def get_stale_rate_statistics(filters, where):
    clickhouse = ClickHouse()
    
    queries = ["""SELECT count(id) as stale_rates FROM brahmastra.fcl_freight_rate_statistics WHERE spot_search_count = 0"""]

    if where:
        queries.append(" AND ")
        queries.append(where)

    charts = jsonable_encoder(clickhouse.execute(" ".join(queries), filters))

    return charts


async def get_missing_rates(filters, where):
    clickhouse = ClickHouse()

    query = [
        """
             WITH
             missing_rates AS (SELECT count(id) as count from brahamstra.fcl_freight_rate_request_statistics WHERE 
             ),
             rate_reverted AS (SELECT count(id) as count from brahamstra.fcl_freight_rate_request_statistics WHERE ),
             spot_search AS (SELECT count(id) as count from brahamstra.fcl_freight_rate_statistics WHERE)
             SELECT * from missing_rates,rate_reverted,spot_search
             """
    ]


async def get_search_to_book_and_feedback_statistics(filters, where):
    clickhouse = ClickHouse()
    queries = [
        """SELECT SUM(spot_search_count) as spot_search,
        SUM(checkout_count) as checkout,
        FLOOR(AVG(1-checkout_count/spot_search_count),2) AS checkoout_percentage,
        SUM(shipment_confirmed_by_service_provider_count) AS shipment_confirmed_by_service_provider,
        FLOOR(AVG(1-shipment_confirmed_by_service_provider_count/checkout_count),2) AS confirmed_booking_percentage,
        SUM(revenue_desk_visit_count) AS revenue_desk_visit,
        FLOOR(AVG(1-revenue_desk_visit_count/shipment_confirmed_by_service_provider_count),2) AS revenue_desk_visit_percentage,
        SUM(so1_visit_count) AS so1_visit,
        FLOOR(AVG(1-so1_visit_count/revenue_desk_visit_count),2) AS so1_visit_percentage,
        SUM(dislikes_count) as dislikes,
        FLOOR(AVG(1-dislikes_count/spot_search_count),2) AS dislikes_percentage,
        SUM(feedback_recieved_count) AS feedback_recieved,
        FLOOR(AVG(1-feedback_recieved_count/dislikes_count),2) AS feedback_recieved_percentage,
        SUM(dislikes_rate_reverted_count) as dislikes_rate_reverted,
        FLOOR(AVG(1-dislikes_rate_reverted_count/feedback_recieved_count),2) AS dislikes_rate_reverted_percentage
        FROM brahmastra.fcl_freight_rate_statistics
        """
    ]

    if where:
        queries.append(" WHERE ")
        queries.append(where)

    if charts := jsonable_encoder(clickhouse.execute(" ".join(queries), filters)):
        return charts[0]
