from services.bramhastra.client import ClickHouse
from services.bramhastra.helpers.fcl_freight_filter_helper import (
    get_direct_indirect_filters,
)
import math
from services.bramhastra.models.fcl_freight_action import FclFreightAction
from services.bramhastra.enums import ShipmentState

async def get_fcl_freight_rate_distribution(filters):
    clickhouse = ClickHouse()

    queries = [
        f"""WITH rate_distribution as 
               (SELECT parent_mode as mode,
               COUNT(CASE WHEN {FclFreightAction.shipment_state.name} = '{ShipmentState.cancelled.name}' THEN 1 END) AS shipment_cancelled_count,
               COUNT(CASE WHEN {FclFreightAction.shipment_state.name} = '{ShipmentState.completed.name}' THEN 1 END) AS shipment_completed_count,
               COUNT(CASE WHEN {FclFreightAction.shipment_state.name} = '{ShipmentState.confirmed_by_importer_exporter.name}' THEN 1 END) AS shipment_confirmed_by_importer_exporter_count,
               COUNT(CASE WHEN {FclFreightAction.shipment_state.name} = '{ShipmentState.aborted.name}' THEN 1 END) AS shipment_aborted_count,
               COUNT(CASE WHEN {FclFreightAction.shipment_state.name} = '{ShipmentState.received.name}' THEN 1 END) AS bookings_created,
               COUNT(CASE WHEN {FclFreightAction.shipment_state.name} = '{ShipmentState.in_progress.name}' THEN 1 END) AS shipment_in_progress_count
               from brahmastra.{FclFreightAction._meta.table_name}"""
    ]

    if where := get_direct_indirect_filters(filters):
        queries.append(" WHERE ")
        queries.append(where)

    queries.append("GROUP BY parent_mode,rate_id")

    total_rate_count = await get_total_rate_count(filters, where)

    queries.append(
        """), mode_count as (SELECT mode,count(mode) as value,
        sum(bookings_created) as bookings_created,
        sum(shipment_cancelled_count + shipment_aborted_count) as shipment_cancelled_count,
        floor((shipment_cancelled_count/bookings_created)*100,2) as shipment_cancelled_percentage,
        sum(shipment_completed_count) as shipment_completed_count,
        floor((shipment_completed_count/bookings_created)*100,2) as shipment_completed_percentage,
        sum(shipment_in_progress_count)  as shipment_in_progress_count,
        floor((shipment_in_progress_count/bookings_created)*100,2) as shipment_in_progress_percentage,
        sum(shipment_confirmed_by_importer_exporter_count)  as shipment_confirmed_by_importer_exporter_count, 
        floor((shipment_confirmed_by_importer_exporter_count/bookings_created)*100,2) as shipment_confirmed_by_importer_exporter_percentage
        from rate_distribution group by mode)
           SELECT * from mode_count"""
    )

    response = clickhouse.execute(" ".join(queries), filters)

    distribution = {}

    format_distribution(response, distribution)

    distribution["total_rate_count"] = total_rate_count

    return distribution


def format_distribution(response, distribution):
    for data in response:
        if data.get('mode') and len(data.get('mode'))>0:
            for k, v in data.items():
                if not isinstance(v, str) and (math.isnan(v) or math.isinf(v)):
                    data[k] = 0
            distribution[data["mode"]] = data
            del data["mode"]


async def get_total_rate_count(filters, where):
    queries = [
        f"SELECT COUNT(DISTINCT rate_id) as count FROM brahmastra.{FclFreightAction._meta.table_name}"
    ]
    if where:
        queries.append("WHERE")
        queries.append(where)

    clickhouse = ClickHouse()
    if result := clickhouse.execute(" ".join(queries), filters):
        return result[0]["count"]
