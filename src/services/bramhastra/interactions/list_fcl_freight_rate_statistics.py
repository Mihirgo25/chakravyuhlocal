from services.bramhastra.client import ClickHouse
from fastapi.encoders import jsonable_encoder
from services.bramhastra.helpers.fcl_freight_filter_helper import (
    get_direct_indirect_filters,add_pagination_data
)
from micro_services.client import maps

DEFAULT_INCUDE_PARAMS = {
    "origin_port_id",
    "destination_port_id",
    "origin_main_port_id",
    "destination_main_port_id",
    "shipping_line_id",
    "service_provider_id",
    "cogo_entity_id",
    "container_size",
    "container_type",
    "commodity",
    "rate_type"
}

LOCATION_KEYS = {'origin_port_id','destination_port_id','origin_main_port_id','destination_main_port_id'}


async def add_service_objects(statistics):
    
    location_ids = set()
    shipping_line_ids = set()
    
    for statistic in statistics:
        for k,v in statistic.items():
            if k in LOCATION_KEYS:
                location_ids.add(v)
            if k == 'shipping_line_id':
                shipping_line_ids.add(v)
    
    shipping_lines = await get_shipping_lines(shipping_line_ids)
    
    locations = await get_locations(location_ids)

    for statistic in statistics:
        update_statistic = dict()
        for k, v in statistic.items():
            if k in LOCATION_KEYS:
                location = locations.get(v)
                if not location:
                    continue
                update_statistic[f"{k[:-3]}"] = location
            if k == 'shipping_line_id':
                shipping_line = shipping_lines.get(v)
                if not shipping_line:
                    continue
                update_statistic['shipping_line'] = shipping_line
        statistic.update(update_statistic)
        
async def get_shipping_lines(ids):
    return {
        shipping_line["id"]: shipping_line
        for shipping_line in maps.list_operators(
            dict(
                filters=dict(id=list(ids)),
                page_limit=len(ids),
            )
        )["list"]
    }
    
    
async def get_locations(ids):
    return {
        location["id"]: location
        for location in maps.list_locations(
            dict(
                filters=dict(id=list(ids)),
                includes=dict(id=True, name=True,port_code = True),
                page_limit=len(ids),
            )
        )["list"]
    }
    

async def list_fcl_freight_rate_statistics(filters,page_limit,page):
    clickhouse = ClickHouse()
    
    select = ','.join(DEFAULT_INCUDE_PARAMS)
    
    queries = [f'''SELECT {select},rate_deviation_from_booking_rate from brahmastra.fcl_freight_rate_statistics''']
    
    if where := get_direct_indirect_filters(filters):
        queries.append("WHERE")
        queries.append(where)
    
    total_count, total_pages = add_pagination_data(
        clickhouse, queries, filters, page, page_limit
    )
    
    queries.insert(0,'WITH list AS (')
    
    queries.append(f') SELECT {select},MAX(rate_deviation_from_booking_rate) as deviation FROM list GROUP BY {select}')
    
    statistics =  jsonable_encoder(clickhouse.execute(' '.join(queries),filters))
    
    await add_service_objects(statistics)
    
    return dict(
        list = statistics,
        page=page,
        page_limit=page_limit,
        total_pages=total_pages,
        total_count=total_count,
    )