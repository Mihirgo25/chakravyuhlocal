from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from configs.definitions import FCL_FREIGHT_LOCAL_CHARGES
from libs.get_applicable_filters import is_valid_uuid
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE
from micro_services.client import *
from database.rails_db import get_operators

def process_conditions(condition_value, condition_key):
    if condition_key in ["origin_country_id", "destination_country_id", "origin_port_id", "terminal_id"]:
        locations_data = maps.list_locations({"filters": {"id": condition_value}})["list"]
        locations_data = [location["name"] for location in locations_data]
        return locations_data
    elif condition_key == "shipping_line_id":
        shipping_line_data = get_operators(id=condition_value)
        shipping_line_data = [shipping_line["short_name"] for shipping_line in shipping_line_data]
        return shipping_line_data


def get_fcl_freight_rate_local_conditions_data(request):
    conditional_data = []
    object = find_object(request)
    data = object.data

    for item in data.get("line_items", []):
        line_item_code = item["code"]
        if "conditions" in item:
            details = {line_item_code: []}
            details["price"] = item["price"]
            details["currency"] = item["currency"]
            conditional_values = item["conditions"]["values"]

            for conditions in conditional_values:
                condition_value = conditions["condition_value"]
                if isinstance(condition_value, str) and  is_valid_uuid(condition_value):
                    new_condition_value = process_conditions([condition_value], conditions["condition_key"])
                    conditions["condition_value"] = new_condition_value
                elif isinstance(condition_value, list):
                    new_condition_value = process_conditions(condition_value, conditions["condition_key"])
                    conditions["condition_value"] = new_condition_value
                details[line_item_code].append(conditions)

            conditional_data.append(details)

    return conditional_data


def find_object(request):
    if request.get("id"):
        object = FclFreightRateLocal.get_by_id(request["id"])
    elif request.get("rate_type") == "cogo_assured":
        object = (
            FclFreightRateLocal.select()
            .where(
                FclFreightRateLocal.port_id == request.get("port_id"),
                FclFreightRateLocal.trade_type == request.get("trade_type"),
                FclFreightRateLocal.rate_type == "cogo_assured",
            )
            .first()
        )
    else:
        object_query = FclFreightRateLocal.select().where(
            FclFreightRateLocal.port_id == request.get("port_id"),
            FclFreightRateLocal.trade_type == request.get("trade_type"),
            FclFreightRateLocal.container_size == request.get("container_size"),
            FclFreightRateLocal.container_type == request.get("container_type"),
            FclFreightRateLocal.shipping_line_id == request.get("shipping_line_id"),
            FclFreightRateLocal.service_provider_id
            == request.get("service_provider_id"),
            FclFreightRateLocal.rate_type == DEFAULT_RATE_TYPE,
            FclFreightRateLocal.commodity == (request.get("commodity") or None),
            FclFreightRateLocal.main_port_id == (request.get("main_port_id") or None),
        )

        object = object_query.first()

    return object
