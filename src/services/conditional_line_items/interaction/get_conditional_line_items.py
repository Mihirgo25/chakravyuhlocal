from services.conditional_line_items.models.conditional_line_items import ConditionalLineItems
from database.db_session import db
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException

def get_conditional_line_items(request,local_rate):
    search_query = ConditionalLineItems.select(
        ConditionalLineItems.data
    ).where(
        ((ConditionalLineItems.port_id == request.get('port_id')) | (ConditionalLineItems.port_id.is_null(True))),
        ((ConditionalLineItems.main_port_id == request.get('main_port_id')) | (ConditionalLineItems.main_port_id.is_null(True))),
        ((ConditionalLineItems.country_id == request.get('country_id')) | (ConditionalLineItems.country_id.is_null(True))),
        ((ConditionalLineItems.shipping_line_id == request.get('shipping_line_id')) | (ConditionalLineItems.shipping_line_id.is_null(True))),
        ((ConditionalLineItems.container_size == request.get('container_size')) | (ConditionalLineItems.container_size.is_null(True))),
        ((ConditionalLineItems.container_type == request.get('container_type')) | (ConditionalLineItems.container_type.is_null(True))),
        ((ConditionalLineItems.commodity == request.get('commodity')) | (ConditionalLineItems.commodity.is_null(True))),
        ConditionalLineItems.trade_type == request.get('trade_type')
    ).dicts()

    conditional_rate = jsonable_encoder(list(search_query.dicts()))

    new_line_items= local_rate['data']['line_items']

    for data in conditional_rate:
        line_items=data.get('data')
        for line_item in line_items:
            if not any(item['code'] == line_item['code'] for item in new_line_items):
                new_line_items.append(line_item)

    return new_line_items