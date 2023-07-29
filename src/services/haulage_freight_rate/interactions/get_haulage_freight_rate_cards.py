import sentry_sdk
import traceback
from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
from services.haulage_freight_rate.interactions.get_trailer_freight_rate_estimations import (
    get_trailer_freight_rate_estimation,
)
from services.haulage_freight_rate.interactions.get_haulage_freight_rate_estimation import (
    get_haulage_freight_rate_estimation,
)
from datetime import datetime, timedelta
from configs.haulage_freight_rate_constants import LOCATION_PAIR_HIERARCHY
from configs.global_constants import CONFIRMED_INVENTORY
from configs.definitions import HAULAGE_FREIGHT_CHARGES
from database.rails_db import (
    get_user,
    get_eligible_orgs,
    list_organization_users,
)
from micro_services.client import common, maps
from libs.json_encoder import json_encoder
from fastapi import HTTPException
from database.rails_db import get_operators


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
        HaulageFreightRate.validity_start,
        HaulageFreightRate.validity_end,
        HaulageFreightRate.service_provider,
        HaulageFreightRate.sourced_by_id
    )
    return freight_query


def initialize_query(requirements, query):
    if requirements.get("origin_location_id") and requirements.get("destination_location_id"):
        origin_location = maps.list_locations({'filters': {'id': requirements.get("origin_location_id")}, "includes": {"default_params_required": 1, "city_id": 1}})['list'][0]
        destination_location = maps.list_locations({'filters': {'id': requirements.get("destination_location_id")},  "includes": {"default_params_required": 1, "city_id": 1}})['list'][0]
        requirements["origin_city_id"] = origin_location['city_id']
        requirements["origin_country_id"] = origin_location['country_id']
        requirements["destination_city_id"] = destination_location['city_id']
        requirements["destination_country_id"] = destination_location['country_id']

    origin_location_ids = [
        requirements.get("origin_location_id"),
        requirements.get("origin_city_id"),
        requirements.get("origin_country_id"),
    ]
    origin_location_ids = list(filter(lambda x: x is not None, origin_location_ids))
    destination_location_ids = [
        requirements.get("destination_location_id"),
        requirements.get("destination_city_id"),
        requirements.get("destination_country_id"),
    ]
    destination_location_ids = list(
        filter(lambda x: x is not None, destination_location_ids)
    )
    if requirements.get("trip_type") == "round":
        requirements["trip_type"] = "round_trip"
    freight_query = query.where(
        HaulageFreightRate.container_type == requirements["container_type"],
        HaulageFreightRate.container_size == requirements["container_size"],
        HaulageFreightRate.commodity == requirements["commodity"],
        HaulageFreightRate.haulage_type == requirements.get("haulage_type"),
        ((
            HaulageFreightRate.importer_exporter_id
            == requirements.get("importer_exporter_id")
        )
        | (HaulageFreightRate.importer_exporter_id.is_null(True))),
        HaulageFreightRate.is_line_items_error_messages_present == False,
        HaulageFreightRate.rate_not_available_entry == False,
    )
    if requirements.get("trip_type"):
        freight_query = freight_query.where(
            HaulageFreightRate.trip_type == requirements["trip_type"]
        )
    if origin_location_ids:
        freight_query = freight_query.where(
            HaulageFreightRate.origin_location_id << origin_location_ids
        )
    if destination_location_ids:
        freight_query = freight_query.where(
            HaulageFreightRate.destination_location_id << destination_location_ids
        )
    if requirements.get("shipping_line_id"):
        freight_query = freight_query.where(
            HaulageFreightRate.shipping_line_id == requirements.get("shipping_line_id")
        )
    if (
        requirements.get("transport_mode")
        and requirements["transport_mode"] != "multimode"
    ):
        freight_query = freight_query.where(
            HaulageFreightRate.transport_modes_keyword
            == requirements.get("transport_mode")
        )
    freight_query = freight_query.where(
        HaulageFreightRate.validity_start <= datetime.now()
        and HaulageFreightRate.validity_end >= datetime.now()
    )
    freight_query = freight_query.where(
        HaulageFreightRate.updated_at >= (datetime.now() - timedelta(days=90)).date()
    )

    return freight_query



def get_query_results(query):
    data = json_encoder(list(query.dicts()))
    return data


def build_line_item_object(line_item, requirements):
    code_config = HAULAGE_FREIGHT_CHARGES[line_item["code"]]

    # checking if additional_service is required in line item
    is_additional_service = code_config["tags"]

    is_additional_service = (
        True if "additional_service" in is_additional_service else False
    )

    if (
        is_additional_service
        and line_item["code"] not in requirements["additional_services"]
    ):
        return None

    # finding slab value
    slab_value = None
    if line_item.get("slabs"):
        if "slab_containers_count" in code_config["tags"]:
            slab_value = requirements["containers_count"]

        if "slab_cargo_weight_per_container" in code_config["tags"]:
            slab_value = requirements["cargo_weight_per_container"]
    # adding line item price currency as per slab value
    if slab_value:
        slabs = line_item["slabs"]
        slab = next(
            (
                s
                for s in slabs
                if s["lower_limit"] <= slab_value and s["upper_limit"] >= slab_value
            ),
            None,
        )
        if slab:
            line_item["price"] = slab["price"]
            line_item["currency"] = slab["currency"]

    # adding other neccessary info name, source
    keys_to_slice = ["code", "unit", "price", "currency", "remarks"]
    line_item = {key: line_item[key] for key in keys_to_slice if key in line_item}
    line_item["quantity"] = (
        requirements["containers_count"]
        if line_item["unit"] in ["per_container"]
        else 1
    )
    line_item["total_price"] = line_item["quantity"] * line_item["price"]
    line_item["name"] = code_config["name"]
    line_item["source"] = "system"

    return line_item


def build_response_object(result, requirements):
    response_object = {
        "id": result["id"],
        "origin_location_id": result["origin_location_id"],
        "destination_location_id": result["destination_location_id"],
        "shipping_line_id": result["shipping_line_id"],
        "importer_exporter_id": result["importer_exporter_id"],
        "service_provider_id": result["service_provider_id"],
        "transport_modes_keyword": result["transport_modes_keyword"],
        "haulage_type": result["haulage_type"],
        "transport_modes": result["transport_modes"],
        "line_items": [],
        "source": "spot_rates" if requirements["predicted_rate"] else "predicted",
        "updated_at": result["updated_at"],
        "tags": [],
        "transit_time": result["transit_time"],
        "detention_free_time": result["detention_free_time"],
        "trailer_type": result.get("trailer_type"),
        "trailer_count": requirements.get("containers_count"),
        "sourced_by_id": result.get("sourced_by_id"),
        "updated_at": result["updated_at"]
    }

    # appeding tags for specific service_provider_id
    if (
        response_object["service_provider_id"]
        in CONFIRMED_INVENTORY["service_provider_ids"]
    ):
        response_object["tags"].append(CONFIRMED_INVENTORY["tag"])

    # additional_services and charge code comparison
    additional_services = requirements["additional_services"]
    if additional_services:
        additional_services = [string.upper() for string in additional_services]
        additional_services = list(filter(None, additional_services))
    charger_codes = []
    for codes in result["line_items"]:
        charger_codes.append(codes["code"])

    if additional_services and list(set(additional_services) - set(charger_codes)):
        return False
    # modifying line items
    for line_item in result["line_items"]:
        if line_item["code"] == "FSC" and line_item["unit"] == "percentage_of_freight":
            for required_line_item in line_item:
                if required_line_item["code"] != "BAS":
                    continue
                line_item["total_price"] = (
                    float(
                        build_line_item_object(required_line_item, requirements)[
                            "total_price"
                        ]
                    )
                    * float(line_item["price"])
                ) / 100
                line_item["quantity"] = requirements["containers_count"]
                line_item["unit"] = "per_trailer"
                line_item["price"] = line_item["total_price"] / line_item["quantity"]
                code_config = HAULAGE_FREIGHT_CHARGES[line_item["code"]]
                line_item["name"] = code_config["name"]
        else:
            line_item = build_line_item_object(line_item, requirements)

        if not line_item:
            continue
        response_object["line_items"].append(line_item)

    return response_object


def build_response_list(requirements, query_results):
    grouping = {}
    query_results = sorted(
            query_results,
            key=lambda t: LOCATION_PAIR_HIERARCHY[
                t["origin_destination_location_type"]
            ],
        )
    for results in query_results:
        if not requirements.get("origin_location_id"):
            key = ":".join([
                results["origin_location_id"],
                results["service_provider_id"] or "",
                results["shipping_line_id"] or "",
                results["haulage_type"] or "",
                results["transport_modes_keyword"] or "",
            ])

        elif not requirements.get("destination_location_id"):
            key = ":".join([
                results["destination_location_id"],
                results["service_provider_id"] or "",
                results["shipping_line_id"] or "",
                results["haulage_type"] or "",
                results["transport_modes_keyword"] or "",
            ])
        else:
            key = ":".join([
                results["service_provider_id"] or "",
                results["shipping_line_id"] or "",
                results["haulage_type"] or "",
                results["transport_modes_keyword"] or "",
            ])
        
        if grouping.get(key) and grouping[key].get('importer_exporter_id'):
            continue

        response_object = build_response_object(results, requirements)
        if response_object:
            grouping[key] = response_object

    return list(grouping.values())

def ignore_non_eligible_service_providers(requirements, data):
    ids = get_eligible_orgs("haulage_freight")
    data = [rate for rate in data if rate.get("service_provider_id") in ids]
    return data


def get_predicted_rate(requirements, data):

    if (
        not data
        and requirements.get("predicted_rate")
        and requirements.get("origin_location_id")
        and requirements.get("destination_location_id")
    ):
        keys_to_slice = [
            "origin_location_id",
            "destination_location_id",
            "container_size",
            "containers_count",
            "container_type",
            "commodity",
            "cargo_weight_per_container",
            "trip_type",
        ]
        estimation_params = {
            key: requirements[key] for key in keys_to_slice if key in requirements
        }
        response = None
        if requirements.get("transport_mode") == "trailer":
            response = get_trailer_freight_rate_estimation(estimation_params)

        elif requirements.get("transport_mode") == "rail":
            response = get_haulage_freight_rate_estimation(estimation_params)

        if response:
            requirements["predicted_rate"] = False
            data = get_haulage_freight_rate_cards(requirements)["list"]

    return data


def ignore_non_active_shipping_lines(data):
    shipping_line_ids = list(set(map(lambda ids: ids["shipping_line_id"], data)))
    shipping_line_ids = [id for id in shipping_line_ids if id is not None]
    if not shipping_line_ids:
        return data
    shipping_line = get_operators(id=shipping_line_ids, operator_type = 'shipping_line')
    shipping_line_ids = list(map(lambda x: x["id"], shipping_line))
    final_data = [
        addon_data
        for addon_data in data
        if not addon_data["shipping_line_id"]
        or addon_data["shipping_line_id"] in shipping_line_ids
    ]

    return final_data


def additional_response_data(data):
    # adding org users
    audit_sourced_by_id = list(map(lambda ids: ids["sourced_by_id"], data))
    org_users = list_organization_users(id=audit_sourced_by_id)

    # adding users
    users = get_user(id=audit_sourced_by_id)

    for addon_data in data:
        if "service_provider" in addon_data:
            addon_data["service_provider_name"] = addon_data["service_provider"].get(
                "short_name"
            )

        user = next(
            filter(lambda t: t["id"] == addon_data["sourced_by_id"], org_users), None
        ) or next(
            filter(lambda t: t["id"] == addon_data["sourced_by_id"], users), None
        )
        
        addon_data["user_name"] = user.get("name")
        addon_data["user_contact"] = user.get("mobile_number") or user.get(
            "mobile_number_eformat"
        )
        
        addon_data["last_updated_at"] = addon_data.get("updated_at")

        addon_data["buy_rate_currency"] = "INR"
        total_price = 0
        for line_item in addon_data["line_items"]:
            total_price += int(
                common.get_money_exchange_for_fcl(
                    {
                        "price": line_item["price"],
                        "from_currency": line_item["currency"],
                        "to_currency": addon_data["buy_rate_currency"],
                    }
                )["price"]
            )
        addon_data["buy_rate"] = total_price
    return data


def get_haulage_freight_rate_cards(requirements):
    """
    Get Haulage Freight Rate Cards
    Returns all eligible rates according to requiremenrs provided

    Response Format
     [{
       id:
       service_provider_id:
       shipping_line_id:
       haulage_type:
       transport_modes_keyword:
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
        # select default required columns
        query = select_fields()

        # initialize query with required conditions
        query = initialize_query(requirements, query)

        # get data from generated query
        query_results = get_query_results(query)

        # ignore non active shipping lines
        list = ignore_non_active_shipping_lines(query_results)

        # ignore non eligible service providers
        list = ignore_non_eligible_service_providers(requirements, list)

        # process and organize query results
        list = build_response_list(requirements, list)

        # get predicted rate in case of not rates
        list = get_predicted_rate(requirements, list)

        # adding additional response data
        if requirements.get("include_additional_response_data"):
            list = additional_response_data(list)
        return {"list": list}

    except Exception as e:
        traceback.print_exc()
        sentry_sdk.capture_exception(e)
        print(e, "Error In Haulage Freight Rate Cards")
        return {"list": []}
