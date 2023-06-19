from services.fcl_cfs_rate.models.fcl_cfs_rate import FclCfsRate
from configs.fcl_cfs_rate_constants import LOCATION_HIERARCHY
from configs.global_constants import CONFIRMED_INVENTORY
from configs.definitions import FCL_CFS_CHARGES
from fastapi.encoders import jsonable_encoder
from database.rails_db import get_eligible_orgs
import traceback, sentry_sdk

def get_fcl_cfs_rate_cards(request):
    try:
        query = initialize_query(request)
        query_results = jsonable_encoder(list(query.dicts()))
        
        if len(query_results) > 0:
            result_list = build_response_list(query_results, request)
            result_list = ignore_non_eligible_service_providers(result_list)

            return {
            "list": result_list
            }

        return {'list':[]} 

    except Exception as e:
        traceback.print_exc()
        sentry_sdk.capture_exception(e)
        print(e, 'Error In Fcl Cfs Rate Cards')
        return {
            "list": []
        }

def ignore_non_eligible_service_providers(freight_rates):
    ids = get_eligible_orgs('fcl_cfs')

    freight_rates = [rate for rate in freight_rates if rate["service_provider_id"] in ids]
    return freight_rates

def initialize_query(request):
    location_ids = list(filter(None, [request.get('port_id'), request.get('country_id')]))
    query = FclCfsRate.select(
        FclCfsRate.line_items,
        FclCfsRate.service_provider_id,
        FclCfsRate.importer_exporter_id,
        FclCfsRate.free_days,
        FclCfsRate.location_type,
        FclCfsRate.mode,
        FclCfsRate.rate_type
    ).where(
        FclCfsRate.location_id << location_ids,
        FclCfsRate.container_size == request.get('container_size'),
        FclCfsRate.container_type == request.get('container_type'),
        FclCfsRate.commodity == request.get('commodity'),
        ((FclCfsRate.importer_exporter_id == request.get('importer_exporter_id')) | (FclCfsRate.importer_exporter_id.is_null(True))),
        FclCfsRate.trade_type == request.get('trade_type'),
        FclCfsRate.is_line_items_error_messages_present == False,
        FclCfsRate.cargo_handling_type == request.get('cargo_handling_type'),
        FclCfsRate.rate_not_available_entry == False
    )

    if request.get('country_id'):
        query = query.where(FclCfsRate.country_id == request['country_id'])

    return query

def build_response_list(query_results, request):
    result_list = []

    grouped_query_results = group_by_service_provider(query_results)
    for key, results in grouped_query_results.items():
        results = sort_results(results)

        customer_specific_rate = find_result_with_importer_exporter(results)
        if not customer_specific_rate:
            customer_specific_rate = results[0]

        response_object = build_response_object(customer_specific_rate, request)

        if response_object:
            result_list.append(response_object)

    return result_list

def group_by_service_provider(query_results):
    grouped_results = {}

    for result in query_results:
        service_provider_id = result.get("service_provider_id")
        if service_provider_id not in grouped_results:
            grouped_results[service_provider_id] = []

        grouped_results[service_provider_id].append(result)
    return grouped_results

def sort_results(results):
    return sorted(results, key=lambda result: LOCATION_HIERARCHY[result.get("location_type")])

def find_result_with_importer_exporter(results):
    for result in results:
        if result["importer_exporter_id"]:
            return result
    return None

def build_response_object(result, request):
    source = 'spot_rates'
    if result.get('mode') == 'predicted':
        source = 'predicted'
    elif result.get('rate_type') != 'market_place':
        source = result.get('rate_type')

    response_object = {
        "service_provider_id": result.get("service_provider_id"),
        "importer_exporter_id": result.get("importer_exporter_id"),
        "line_items": [],
        "free_days": [free_day | {"unit": "per_day"} for free_day in result.get("free_days",[])],
        "source": source,
        "tags": []
    }

    if result.get("service_provider_id") in CONFIRMED_INVENTORY["service_provider_ids"]:
        response_object["tags"].append(CONFIRMED_INVENTORY["tag"])

    if not add_cfs_charges(result, response_object, request):
        return 
    
    if not response_object["line_items"]:
        return None

    return response_object
    
def add_cfs_charges(result, response_object, request):
    if not result.get("line_items"):
        return False

    for line_item in result.get("line_items",[]):
        line_item = build_line_item_object(line_item,request)

        if line_item:
            response_object["line_items"].append(line_item)

    return True

def build_line_item_object(line_item, request):
    code_config = FCL_CFS_CHARGES.get(line_item["code"])

    if not code_config:
        return None

    is_additional_service = "additional_service" in code_config.get("tags", [])
    if is_additional_service and line_item["code"] not in request.get('additional_services'):
        return None

    if request.get('cargo_handling_type') not in code_config.get("tags", []):
        return None

    slab_value = None
    if line_item.get("slabs") and "slab_cargo_weight_per_container" in code_config.get("tags", []):
        slab_value = request.get('cargo_weight_per_container')

    if slab_value is not None:
        slab = next((slab for slab in line_item["slabs"] if slab["lower_limit"] <= slab_value <= slab["upper_limit"]), None)
        if slab is not None:
            line_item["price"] = slab["price"]
            line_item["currency"] = slab["currency"]

    line_item = {
        'code':line_item.get('code'),
        'unit':line_item.get('unit'),
        'price':line_item.get('price'),
        'currency':line_item.get('currency'),
        'remarks':line_item.get('remarks')
    }
    if line_item.get("unit") == "cargo_value_percentage" and request.get('cargo_value'):
        line_item["currency"] = request.get('cargo_value_currency')
        line_item["price"] = (request.get('cargo_value') * line_item.get('price'))/100

    line_item['quantity'] = request.get('containers_count') if line_item['unit'] == 'per_container' else 1
    line_item['total_price'] = line_item['quantity'] * line_item['price']
    line_item['name'] = code_config.get('name')
    line_item['source'] = 'system'

    return line_item