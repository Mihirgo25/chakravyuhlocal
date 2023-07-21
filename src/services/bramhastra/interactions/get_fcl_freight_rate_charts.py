from services.bramhastra.helpers.get_fcl_freight_rate_helper import ClickHouse
from fastapi.encoders import jsonable_encoder

POSSIBLE_DIRECT_FILTERS = {
    "origin_port_id",
    "origin_country_id",
    "origin_trade_id",
    "origin_continent_id",
    "destination_port_id",
    "destination_country_id",
    "destination_trade_id",
    "destination_continent_id",
    "shipping_line_id",
    "service_provider_id",
    "importer_exporter_id",
    "container_size",
    "container_type",
    "commodity",
    "origin_main_port_id",
    "destination_main_port_id",
    "procured_by_id",
    "rate_type",
    "mode",
    "sourced_by_id",
    "procured_by_id",
}

POSSIBLE_INDIRECT_FILTERS = {"start_date", "end_date"}

NEEDED_MODES = {"rate_extension", "cluster_extension", "predicted", "manual"}


async def get_fcl_freight_rate_stats(filters):
    where = get_direct_indirect_filters(filters)
    accuracy = await get_accuracy(filters, where)
    deviation = await get_deviation(filters, where)
    return dict(accuracy=accuracy, deviation=deviation)


async def get_accuracy(filters, where):
    clickhouse = ClickHouse()
    queries = [
        """SELECT mode,toStartOfInterval(created_at,INTERVAL 19 DAY) as day,AVG(price) AS average_price FROM brahmastra.fcl_freight_rate_statistics"""
    ]

    if where:
        queries.append(" WHERE ")
        queries.append(where)

    queries.append(
        """GROUP BY day,mode ORDER BY day WITH FILL STEP toIntervalDay(19);"""
    )

    charts = jsonable_encoder(clickhouse.execute(" ".join(queries), filters))

    return format_charts(charts)


async def get_deviation(filters, where):
    clickhouse = ClickHouse()
    queries = [
        """SELECT CASE
                WHEN price BETWEEN -100 AND -80 THEN -80
                WHEN price BETWEEN -79 AND -60 THEN -60
                WHEN price BETWEEN -59 AND -40 THEN -40
                WHEN price BETWEEN -39 AND -20 THEN -20
                WHEN price BETWEEN -20 AND 0 THEN 0
                WHEN price BETWEEN 1 AND 20 THEN 20
                WHEN price BETWEEN 21 AND 40 THEN 40
                WHEN price BETWEEN 41 AND 60 THEN 60
                WHEN price BETWEEN 61 AND 80 THEN 80
                WHEN price BETWEEN 81 AND 100 THEN 100
            END AS range,
            COUNT(1) AS count
            FROM brahmastra.fcl_freight_rate_statistics"""
    ]

    if where:
        queries.append(" WHERE ")
        queries.append(where)

    queries.append("GROUP BY range ORDER BY range WITH FILL FROM -80 TO 100 STEP 20;")

    response = clickhouse.execute(" ".join(queries), filters)
    
    return [i for i in response if i['range'] or i['range'] == 0]  # remove this later
            


def get_direct_indirect_filters(filters):
    if not filters:
        return
    where = []
    for key in filters.keys():
        if key in POSSIBLE_DIRECT_FILTERS:
            where.append(f"{key} = %({key})s")
        if key in POSSIBLE_INDIRECT_FILTERS:
            eval(f"get_{key}_filter(where)")

    if where:
        return " AND ".join(where)


def get_start_date_filter(where):
    where.append("validity_start >= %(start_date)s")


def get_end_date_filter(queries):
    queries.append("validity_end <= %(end_date)s")


def format_charts(charts):
    formatted_charts = dict(manual = {
        'id': 'supply_rates',
        'data': []
    },
    rate_extension = {
        'id': 'rate_extension',
        'data': []
    },
    cluster_extension = {
        'id': 'cluster_extension',
        'data': []
    },
    predicted = {
        'id': 'predicted',
        'data': []
    })
    
    previous_day = None
    for chart in charts:
        if not previous_day:
            previous_day = chart['day']
            needed_modes = NEEDED_MODES.copy()
        elif previous_day != chart['day']:
            for mode in needed_modes:
                 formatted_charts[mode]['data'].append(dict(x = chart['day'],y = 0))
                 needed_modes = NEEDED_MODES.copy()
                 previous_day = chart['day']
            continue

        if chart['average_price']:
            formatted_charts[chart['mode']]['data'].append(dict(x = chart['day'],y = chart['average_price']))
            needed_modes.remove(chart['mode'])
        else:
            for mode in needed_modes:
                formatted_charts[mode]['data'].append(dict(x = chart['day'],y = 0))
            
        
    return list(formatted_charts.values())