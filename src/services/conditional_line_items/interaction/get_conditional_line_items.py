from services.conditional_line_items.models.conditional_line_items import ConditionalLineItems
from database.db_session import db
from fastapi import HTTPException

def get_conditional_line_items(request):
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

    for i in search_query:
        print(i)
    print(search_query)