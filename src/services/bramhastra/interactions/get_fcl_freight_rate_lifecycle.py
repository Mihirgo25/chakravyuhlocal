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
        FLOOR((1-SUM(checkout_count)/SUM(spot_search_count)),2)*100 AS checkoout_percentage,
        SUM(shipment_confirmed_by_service_provider_count) AS shipment_confirmed_by_service_provider,
        FLOOR((1-SUM(shipment_confirmed_by_service_provider_count)/SUM(checkout_count)),2)*100 AS confirmed_booking_percentage,
        SUM(revenue_desk_visit_count) AS revenue_desk_visit,
        FLOOR((1-SUM(revenue_desk_visit_count)/SUM(shipment_confirmed_by_service_provider_count)),2)*100 AS revenue_desk_visit_percentage,
        SUM(so1_visit_count) AS so1_visit,
        FLOOR((1-SUM(so1_visit_count)/SUM(revenue_desk_visit_count)),2)*100 AS so1_visit_percentage,
        SUM(dislikes_count) as dislikes,
        FLOOR((1-SUM(dislikes_count)/SUM(spot_search_count)),2)*100 AS dislikes_percentage,
        SUM(feedback_recieved_count) AS feedback_recieved,
        FLOOR((1-SUM(feedback_recieved_count)/SUM(dislikes_count)),2)*100 AS feedback_recieved_percentage,
        SUM(dislikes_rate_reverted_count) as dislikes_rate_reverted,
        FLOOR((1-SUM(dislikes_rate_reverted_count)/SUM(feedback_recieved_count)),2)*100 AS dislikes_rate_reverted_percentage
        FROM brahmastra.fcl_freight_rate_statistics
        """
    ]

    if where:
        queries.append(" WHERE ")
        queries.append(where)

    if charts := jsonable_encoder(clickhouse.execute(" ".join(queries), filters)):
        return charts[0]
