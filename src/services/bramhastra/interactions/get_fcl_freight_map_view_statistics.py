from services.bramhastra.helpers.get_fcl_freight_rate_helper import ClickHouse
from services.bramhastra.helpers.filter_helper import get_direct_indirect_filters
from fastapi.encoders import jsonable_encoder
from micro_services.client import maps

HEIRARCHY = ["continent", "country", "region", "port"]

LOCATION_KEYS = {
    "origin_port_id",
    "origin_country_id",
    "origin_trade_id",
    "origin_continent_id",
    "destination_port_id",
    "destination_country_id",
    "destination_trade_id",
    "destination_continent_id",
    "origin_region_id",
    "destination_region_id",
}


async def add_location_objects(statistics):
    location_ids = []
    for statistic in statistics:
        for k, v in statistic:
            if k in LOCATION_KEYS:
                location_ids.append(v)

    locations = {
        location["id"]: location["display_name"]
        for location in maps.list_locations(
            dict(
                filters=dict(id=location_ids), includes=dict(id=True, display_name=True)
            )
        )["list"]
    }

    for statistic in statistics:
        for k, v in statistic:
            if k in LOCATION_KEYS:
                statistic[k[:-3]] = locations[v]
                
async def add_shipping_line_objects(statistics):
    operator_ids = []
    for statistic in statistics:
        for k, v in statistic:
            if k in LOCATION_KEYS:
                operator_ids.append(v)

    operators = {
        operator["id"]: operator["display_name"]
        for operator in maps.list_operators(
            dict(
                filters=dict(id=operator_ids), includes=dict(id=True, short_name=True)
            )
        )["list"]
    }

    for statistic in statistics:
        for k, v in statistic:
            if k in LOCATION_KEYS:
                statistic[k[:-3]] = operators[v]


async def get_fcl_freight_map_view_statistics(filters):
    click_house = ClickHouse()

    grouping = set()

    alter_filters_for_map_view(filters, grouping)

    queries = [
        f'SELECT {",".join(grouping)},abs(AVG(accuracy)) as accuracy FROM brahmastra.fcl_freight_rate_statistics'
    ]

    if where := get_direct_indirect_filters(filters):
        queries.append(" WHERE ")
        queries.append(where)

    get_add_group_and_order_by(queries, grouping)

    statistics = click_house.execute(" ".join(queries), filters)

    statistics = jsonable_encoder(statistics)

    await add_location_objects(statistics)
    
    await add_shipping_line_objects(statistics)

    return statistics


def get_add_group_and_order_by(queries, grouping):
    queries.append("GROUP BY")
    queries.append(",".join(grouping))
    queries.append("ORDER BY accuracy")


def alter_filters_for_map_view(filters, grouping):
    if "origin" in filters:
        index_to_look = HEIRARCHY.index(filters["origin"]["type"]) + 1
        origin_key = f"origin_{filters['origin']['type']}_id"
        destination_key = f"destination_{filters['destination']['type']}_id"
        filters[origin_key] = filters["origin"]["id"]
        filters[destination_key] = filters["destination"]["id"]
        if index_to_look <= len(HEIRARCHY) - 1 and "destination" in filters:
            if filters["destination"]["type"] == filters["origin"]["type"]:
                origin_key = f"origin_{HEIRARCHY[index_to_look]}_id"
                destination_key = f"destination_{HEIRARCHY[index_to_look]}_id"
            else:
                destination_index_to_look = (
                    HEIRARCHY.index(filters["destination"]["type"]) + 1
                )
                if destination_index_to_look <= len(HEIRARCHY) - 1:
                    destination_key = (
                        f"destination_{HEIRARCHY[destination_index_to_look]}_id"
                    )

            filters.pop("destination")

        grouping.add(origin_key)
        grouping.add(destination_key)
        filters.pop("origin")