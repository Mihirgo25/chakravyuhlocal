from services.conditional_line_items.models.conditional_line_items import ConditionalLineItems
from database.db_session import db
from fastapi import HTTPException

def create_conditional_line_items(request):
    with db.atomic():
        return execute_transaction_code(request)


def execute_transaction_code(request):
    row = {
        "port_id": request.get("port_id"),
        "main_port_id": request.get("main_port_id"),
        "country_id": request.get("country_id"),
        "shipping_line_id":request.get("shipping_line_id"),
        "container_size": request.get("container_size"),
        "container_type": request.get("container_type"),
        "commodity": request.get("commodity"),
        "trade_type":request.get("trade_type"),
        "status":'active',
        "charge_code":request.get("charge_code"),
        "data": request.get("data")
    }

    condition_items = (
        ConditionalLineItems.select(
            ConditionalLineItems.charge_code,
            ConditionalLineItems.data
        )
        .where(
            ConditionalLineItems.port_id == request.get("port_id"),
            ConditionalLineItems.main_port_id == request.get("main_port_id"),
            ConditionalLineItems.country_id == request.get("country_id"),
            ConditionalLineItems.shipping_line_id == request.get("shipping_line_id"),
            ConditionalLineItems.commodity == request.get("commodity"),
            ConditionalLineItems.trade_type == request.get("trade_type"),
            ConditionalLineItems.container_size == request.get("container_size"),
            ConditionalLineItems.container_type == request.get("container_type"),
            ConditionalLineItems.status == request.get('status')
        )
        .first()
    )

    if not condition_items:
        condition_items = ConditionalLineItems()
        for key in list(row.keys()):
            setattr(condition_items, key, row[key])

    try:
        condition_items.save()
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
    
    audit_params = get_audit_params(request, condition_items)
    
    condition_items.create_audit(audit_params)
    
    return {
        "id": condition_items.id
    }

def get_audit_params(request, rate):    
    return {
        "object_id": rate.id,
        "action_name": "create",
        "data": request.get("data"),
        "rate_sheet_id":request.get('rate_sheet_id'),
        "performed_by_id": request.get('performed_by_id')
    }