from services.fcl_cfs_rate.models.fcl_cfs_rate import FclCfsRate
from configs.fcl_cfs_rate_constants import LOCATION_HIERARCHY
from configs.global_constants import PREDICTED_RATES_SERVICE_PROVIDER_IDS,CONFIRMED_INVENTORY
from configs.definitions import FCL_CFS_CHARGES

def get_fcl_cfs_rate_card(trade_type, cargo_handling_type, port_id, country_id,
                             container_size, container_type, commodity, importer_exporter_id,
                             containers_count, bls_count, cargo_weight_per_container,
                             additional_services, cargo_value, cargo_value_currency,
                             include_confirmed_inventory_rates):
    
    query = initialize_query(trade_type, cargo_handling_type, port_id, country_id,
                             container_size, container_type, commodity, importer_exporter_id,
                             containers_count, bls_count, cargo_weight_per_container,
                             additional_services, cargo_value, cargo_value_currency,
                             include_confirmed_inventory_rates)

    query_results = get_query_results(query)

    result_list = build_response_list(query_results)

    result_list = ignore_non_eligible_service_providers(result_list)

    return {
        "list": result_list
    }

def ignore_non_eligible_service_providers(result_list):
    return result_list



def initialize_query(trade_type, cargo_handling_type, port_id, country_id,
                     container_size, container_type, commodity, importer_exporter_id,
                     containers_count, bls_count, cargo_weight_per_container,
                     additional_services, cargo_value, cargo_value_currency,
                     include_confirmed_inventory_rates):
    query = FclCfsRate.select().where(
        (FclCfsRate.location_id == port_id) &
        (FclCfsRate.container_size == container_size) &
        (FclCfsRate.container_type == container_type) &
        (FclCfsRate.commodity == commodity) &
        (FclCfsRate.importer_exporter_id.in_([None, importer_exporter_id])) &
        (FclCfsRate.trade_type == trade_type) &
        (FclCfsRate.is_line_items_error_messages_present == False) &
        (FclCfsRate.cargo_handling_type == cargo_handling_type) &
        (FclCfsRate.rate_not_available_entry == False)
    )

    if country_id:
        query = query.where(FclCfsRate.location_id == country_id)
    #print(query)
    return query
def get_query_results(query):
    query_results = query.dicts()

    return list(query_results)

def build_response_list(query_results):
    result_list = []

    grouped_query_results = group_by_service_provider(query_results)
    for _, results in grouped_query_results.items():
        results = sort_results(results)

        result = find_result_with_importer_exporter(results)
        if result is None:
            result = results[0]

        response_object = build_response_object(result)

        if response_object is not None:
            result_list.append(response_object)

    return result_list
def group_by_service_provider(query_results):
    grouped_results = {}

    for result in query_results:
        service_provider_id = result["service_provider_id"]
        if service_provider_id not in grouped_results:
            grouped_results[service_provider_id] = []

        grouped_results[service_provider_id].append(result)

    return grouped_results

def sort_results(results):
    return sorted(results, key=lambda result: LOCATION_HIERARCHY[result["location_type"]])

def find_result_with_importer_exporter(results):
    for result in results:
        if result["importer_exporter_id"]:
            return result

    return None

def build_response_object(result):
    response_object = {
        "service_provider_id": result["service_provider_id"],
        "importer_exporter_id": result["importer_exporter_id"],
        "line_items": [],
        "free_days": [free_day | {"unit": "per_day"} for free_day in result["free_days"]],
        "source": "predicted" if result["service_provider_id"] in PREDICTED_RATES_SERVICE_PROVIDER_IDS else "spot_rates",
        "tags": []
    }

    if result["service_provider_id"] in CONFIRMED_INVENTORY["service_provider_ids"]:
        response_object["tags"].append(CONFIRMED_INVENTORY["tag"])

    if add_cfs_charges(result, response_object):
        if not response_object["line_items"]:
            return None

        return response_object
def add_cfs_charges(result, response_object):
    if not result["line_items"]:
        return False

    for line_item in result["line_items"]:
        line_item = build_line_item_object(line_item,additional_services,cargo_handling_type,cargo_weight_per_container,cargo_value,cargo_value_currency)

        if line_item is not None:
            response_object["line_items"].append(line_item)

    return True

def build_line_item_object(line_item,additional_services,cargo_handling_type,cargo_weight_per_container,cargo_value,cargo_value_currency):
    code_config = FCL_CFS_CHARGES.get(line_item["code"])

    if code_config is None:
        return None

    is_additional_service = "additional_service" in code_config.get("tags", [])
    if is_additional_service and line_item["code"] not in additional_services:
        return None

    if cargo_handling_type not in code_config.get("tags", []):
        return None

    slab_value = None
    if line_item["slabs"] and "slab_cargo_weight_per_container" in code_config.get("tags", []):
        slab_value = cargo_weight_per_container

    if slab_value is not None:
        slab = next((slab for slab in line_item["slabs"] if slab["lower_limit"] <= slab_value <= slab["upper_limit"]), None)
        if slab is not None:
            line_item["price"] = slab["price"]
            line_item["currency"] = slab["currency"]

    line_item = {key: line_item[key] for key in ["code", "unit", "price", "currency", "remarks"]}
    if line_item["unit"] == "cargo_value_percentage" and cargo_value is not None:
        line_item["currency"] = cargo_value_currency