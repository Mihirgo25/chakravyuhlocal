import sentry_sdk
import traceback
from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
from datetime import datetime, timedelta
from configs.haulage_freight_rate_constants import LOCATION_PAIR_HIERARCHY
from configs.global_constants import CONFIRMED_INVENTORY
from configs.definitions import HAULAGE_FREIGHT_CHARGES



def initialize_query(requirements, query):
    origin_location_ids = [
        requirements.get("origin_location_id"),
        requirements.get("origin_city_id"),
        requirements.get("origin_country_id"),
    ]
    destination_location_ids = [
        requirements.get("destination_location_id"),
        requirements.get("destination_city_id"),
        requirements.get("destination_country_id"),
    ]
    if requirements.get("trip_type") == "round":
        requirements["trip_type"] = "round_trip"

    freight_query = query.where(
        HaulageFreightRate.container_type == requirements["container_type"],
        HaulageFreightRate.container_size == requirements["container_size"],
        HaulageFreightRate.commodity == requirements["commodity"],
        HaulageFreightRate.haulage_type == requirements.get("haulage_type"),
        HaulageFreightRate.importer_exporter_id
        << [None, requirements.get("importer_exporter_id")],
        HaulageFreightRate.is_line_items_error_messages_present == False,
        HaulageFreightRate.rate_not_available_entry == False
    )
    if requirements.get('trip_type'):
        freight_query = freight_query.where(HaulageFreightRate.trip_type == requirements['trip_type'])
    if origin_location_ids:
        freight_query = freight_query.where(HaulageFreightRate.origin_location_id == origin_location_ids)
    if destination_location_ids:
        freight_query = freight_query.where(HaulageFreightRate.destination_location_id == destination_location_ids)
    if requirements.get('shipping_line_id'):
        freight_query = freight_query.where(HaulageFreightRate.shipping_line_id == requirements.get('shipping_line_id'))
    if requirements.get('transport_mode') and requirements['transport_mode'] != 'multimode':
        freight_query = freight_query.where(HaulageFreightRate.transport_modes_keyword == requirements.get('transport_mode'))
    if requirements.get('transport_mode') == 'trailer':
        freight_query = freight_query.where(HaulageFreightRate.validity_start <= datetime.now() and HaulageFreightRate.validity_end >= datetime.now())
    freight_query = freight_query.where(HaulageFreightRate.updated_at >= (datetime.now() - timedelta(days=90)).date())

    return freight_query

def select_fields():
    freight_query = HaulageFreightRate.select(
    HaulageFreightRate.id,
    HaulageFreightRate.commodity,
    HaulageFreightRate.line_items,
    HaulageFreightRate.service_provider_id,
    HaulageFreightRate.shipping_line_id,
    HaulageFreightRate.importer_exporter_id,
    HaulageFreightRate.transport_modes,
    HaulageFreightRate.haulage_type,
    HaulageFreightRate.transport_modes_keyword,
    HaulageFreightRate.origin_location_id,
    HaulageFreightRate.destination_location_id,
    HaulageFreightRate.origin_destination_location_type,
    HaulageFreightRate.updated_at,
    HaulageFreightRate.transit_time,
    HaulageFreightRate.detention_free_time,
    HaulageFreightRate.service_provider_id
    )
    return freight_query
    
def get_query_results(query):
    data = list(query.dicts())
    return data

def build_line_item_object(line_item, requirements):
    code_config = HAULAGE_FREIGHT_CHARGES[line_item["code"]]
    try:
        is_additional_service = code_config["tags"].get("additional_service")
    except:
        return False
    if is_additional_service and requirements["additional_services"].get(line_item["code"]):
        return
    slab_value = None
    return 

def build_response_object(result, requirements):
    response_object = {
        "id" : result["id"],
        "origin_location_id" : result["origin_location_id"],
        "destination_location_id" : result["destination_location_id"],
        "shipping_line_id" : result["shipping_line_id"],
        "importer_exporter_id" : result["importer_exporter_id"],
        "service_provider_id" : result["service_provider_id"],
        "transport_modes_keyword" : result["transport_modes_keyword"],
        "haulage_type" : result["haulage_type"],
        "transport_modes" : result["transport_modes"],
        "line_items" : [],
        "source" : "spot_rates" if requirements["predicted_rate"] else 'predicted',
        "updated_at" : result["updated_at"],
        "tags" : [],
        "transit_time" : result["transit_time"],
        "detention_free_time" : result["detention_free_time"],
    }
    if response_object["service_provider_id"] in CONFIRMED_INVENTORY["service_provider_ids"]:
        response_object["tags"].append(CONFIRMED_INVENTORY["tags"])
    additional_services = requirements["additional_services"]
    # why is there a upcase here
    if additional_services - result["line_items"][0]['code']:
        return False
    # very doubbtful
    for line_item  in result['line_item']:
        if line_item["code"] == 'FSC' and line_item["unit"] == 'percentage_of_freight':
            for required_line_item in line_item:
                if required_line_item["code"] != "BAS":
                    continue
                line_item["total_price"] = build_line_item_object()



def build_response_list(requirements, query_results):
    list = []
    if not requirements.get('origin_location_id'):
        grouped_query_results = {}

        for result in query_results:
            key = tuple(result[key] for key in ["origin_location_id", "service_provider_id", "shipping_line_id", "haulage_type", "transport_modes_keyword"])
            if key not in grouped_query_results:
                grouped_query_results[key] = []
            grouped_query_results[key].append(result)
        grouped_query_results = query_results
    elif not requirements.get('destination_location_id'):
        grouped_query_results = query_results
    else:
        grouped_query_results = query_results

    for key, results in grouped_query_results.items():
        results = sorted(results, key=lambda t: LOCATION_PAIR_HIERARCHY[t['origin_destination_location_type']])
        result = results[0].get('importer_exporter_id')
        if not result:
            result = results[0]
        response_object = build_response_object(result, requirements)
        if response_object:
            list.append(response_object)

    return list

def get_haulage_freight_rate_cards(requirements):
    """
     Returns all eligible rates according to requiremenrs provided

     Response Format
     [{
       id:
       service_provider_id:
       shipping_line_id:
       haulage_type:
       transport_mode_keyword:
       transport_modes:
       transit_time:
       detention_free_time:
       validity_start:
       validity_end:
         line_items: [{
         name:
         code:
         unit:
         quantity:
         price:
         total_price:
         currency:
         remarks:
     }]
    }]
    """
    try:
        query = select_fields(requirements)
        query = initialize_query(requirements, query)
        query_results = get_query_results(query)
        list = build_response_list(requirements, query_results)

    except Exception as e:
        traceback.print_exc()
        sentry_sdk.capture_exception(e)
        print(e, "Error In Haulage Freight Rate Cards")
        return {"list": []}
