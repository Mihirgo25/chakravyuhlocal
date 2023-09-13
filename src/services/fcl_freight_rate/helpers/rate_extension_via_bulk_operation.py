from configs.env import DEFAULT_USER_ID

from configs.fcl_freight_rate_constants import DEFAULT_PERFORMED_BY_TYPE
from datetime import datetime, timedelta
ACTION_NAMES_FOR_SOURCES = {
    "flash_booking": "extend_freight_rate",
    "latest_rate_trend": "add_freight_rate_markup",
}

def rate_extension_via_bulk_operation(request):
    from services.fcl_freight_rate.interaction.create_fcl_freight_rate_bulk_operation import create_fcl_freight_rate_bulk_operation

    source = request.get("source")
    if source in ACTION_NAMES_FOR_SOURCES:
        bulk_operation_params = eval("get_"+ACTION_NAMES_FOR_SOURCES[source]+"_params"+"(request)")
        id = create_fcl_freight_rate_bulk_operation(bulk_operation_params)
        return True
    else:
        return False

def get_extend_freight_rate_params(request):
    data = {}
    data["filters"] = {
        "origin_port_id": request.get("origin_port_id"),
        "origin_main_port_id": request.get("origin_main_port_id"),
        "destination_port_id": request.get("destination_port_id"),
        "destination_main_port_id": request.get("destination_main_port_id"),
        "container_size": request.get("container_size"),
        "container_type": request.get("container_type"),
        "commodity": request.get("commodity"),
        "shipping_line_id": request.get("shipping_line_id")
    }
    data["line_item_code"] = "BAS"
    data["markup_type"] = "absolute"
    data["markup"] = [val["price"] for val in request.get("line_items") if val["code"] == "BAS"][0]
    data["extend_for_flash_booking"] = True
    
    params = {}
    params["performed_by_type"] = "agent"
    params["performed_by_id"] = DEFAULT_USER_ID
    params["procured_by_id"] = DEFAULT_USER_ID
    params["sourced_by_id"] = DEFAULT_USER_ID
    params["extend_freight_rate"] = data
    params["created_at"] = datetime.now()
    params["updated_at"] = datetime.now()
    
    return params

def get_add_freight_rate_markup_params(request):
    data = {}
    data["filters"] = request.get('filters') or {}
    data["line_item_code"] = "BAS"
    data["tag"] = "trend_GRI"
    data["markup_type"] = "percent"
    data["markup"] = request.get("markup")
    data["markup_currency"] = "USD"
    data["validity_start"] = datetime.now() - timedelta(days=3)
    data["validity_end"] = datetime.now() + timedelta(days=60)
    data["min_allowed_markup"] = request.get("min_allowed_markup")
    data["max_allowed_markup"] = request.get("max_allowed_markup")
    data["affect_market_price"] = False
    data["rate_sheet_serial_id"] = None
    data["apply_to_extended_rates"] = False
    data["rates_greater_than_price"] = None
    data["rates_less_than_price"] = None
    data["is_system_operation"] = True
    params = {}
    params["performed_by_type"] = DEFAULT_PERFORMED_BY_TYPE
    params["performed_by_id"] = DEFAULT_USER_ID
    params["procured_by_id"] = DEFAULT_USER_ID
    params["sourced_by_id"] = DEFAULT_USER_ID
    params["add_freight_rate_markup"] = data
    params["created_at"] = datetime.now()
    params["updated_at"] = datetime.now()
    
    return params