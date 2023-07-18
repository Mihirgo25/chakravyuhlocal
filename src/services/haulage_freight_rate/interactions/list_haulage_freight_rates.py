from playhouse.postgres_ext import SQL
import json, uuid, math
from libs.get_filters import get_filters
from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
import services.haulage_freight_rate.interactions.list_haulage_freight_rates as list_haulage_freight_rate
from libs.get_applicable_filters import get_applicable_filters
from libs.json_encoder import json_encoder
from micro_services.client import common


POSSIBLE_DIRECT_FILTERS = [
    "id",
    "origin_location_id",
    "destination_location_id",
    "container_size",
    "container_type",
    "commodity",
    "haulage_type",
    "shipping_line_id",
    "service_provider_id",
    "importer_exporter_id",
    "shipping_line_id",
    "trailer_type",
    "transport_modes_keyword",
    "procured_by_id",
    "transport_modes",
    "origin_location_ids",
    "destination_location_ids",
]


POSSIBLE_INDIRECT_FILTERS = [
    "is_rate_available",
]


DEFAULT_PARAMS = [
    "commodity",
    "container_size",
    "container_type",
    "containers_count",
    "created_at",
    "destination_city_id",
    "destination_cluster_id",
    "destination_country_id",
    "destination_location_id",
    "destination_location_type",
    "detention_free_time",
    "haulage_type",
    "id",
    "importer_exporter",
    "importer_exporter_id",
    "is_best_price",
    "is_line_items_error_messages_present",
    "is_line_items_info_messages_present",
    "line_items",
    "line_items_error_messages",
    "line_items_info_messages",
    "origin_city_id",
    "origin_cluster_id",
    "origin_country_id",
    "origin_destination_location_type",
    "origin_location_id",
    "origin_location_type",
    "platform_price",
    "procured_by_id",
    "rate_not_available_entry",
    "service_provider_id",
    "shipping_line_id",
    "sourced_by_id",
    "trailer_type",
    "transit_time",
    "transport_modes",
    "transport_modes_keyword",
    "trip_type",
    "updated_at",
    "validity_end",
    "validity_start",
    "weight_slabs",
    "sourced_by",
    "procured_by",
    "service_provider",
    "shipping_line",
    "origin_location",
    "destination_location",
    "trailer_type",
    "transit_time",
    "origin_location_ids",
    "destination_location_ids"
]


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def apply_direct_filters(query, filters):
    query = get_filters(filters, query, HaulageFreightRate)
    return query


def apply_indirect_filters(query, filters):
    for key, val in filters.items():
        query = getattr(list_haulage_freight_rate, "apply_{}_filter".format(key))(
            query, val, filters
        )
    return query


def apply_pagination(query, page, page_limit):
    offset = (page - 1) * page_limit
    total_count = query.count()
    query = query.order_by(SQL("updated_at desc"))
    query = query.offset(offset).limit(page_limit)
    return query, total_count


def filter_preferences(filters):
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)
    return filters

def add_pagination_data(
    response, page, total_count, page_limit, final_data, pagination_data_required
):
    if pagination_data_required:
        response["page"] = page
        response["total"] = math.ceil(total_count / page_limit)
        response["total_count"] = total_count
        response["page_limit"] = page_limit
    response["success"] = True
    response["list"] = final_data
    return response


def add_service_objects(data):
    for object in data:
        object["total_price_currency"] = 'INR'
        total_price = 0
        for line_item in object["line_items"]:
            total_price += common.get_money_exchange_for_fcl({"price": line_item['price'], "from_currency": line_item['currency'], "to_currency": object['total_price_currency'] })['price']
        object["total_price"] = total_price
        try:
            if 'display_name' not in object['destination_location']:
                object['destination_location']['display_name'] = object['destination_location']['name']
            if 'display_name' not in object['origin_location']:
                object['origin_location']['display_name'] = object['origin_location']['name']
        except:
            continue
    return data


def get_final_data(query):
    raw_data = json_encoder(list(query.dicts()))
    return raw_data


def apply_is_rate_available_filter(query, val, filters):
    query = query.where(HaulageFreightRate.rate_not_available_entry == False)
    return query

def get_query(sort_by, sort_type, includes):
    fields = [getattr(HaulageFreightRate, key) for key in DEFAULT_PARAMS]

    if includes and  not isinstance(includes, dict):
        includes = json.loads(includes)
    
    query = HaulageFreightRate.select(*fields)

    if sort_by:
        query = query.order_by(eval('FclFreightRate.{}.{}()'.format(sort_by,sort_type)))

    return query

def list_haulage_freight_rates(
    filters={}, includes = {}, page_limit=10, page=1, sort_by= 'updated_at', sort_type = 'desc',  pagination_data_required=True
):
    response = {"success": False, "status_code": 200}

    # filters
    filters = filter_preferences(filters)


    # applying sorting filters
    query = get_query(sort_by, sort_type, includes)


    # direct and indirect filters

    if filters:
        direct_filters, indirect_filters = get_applicable_filters(
            filters, POSSIBLE_DIRECT_FILTERS, POSSIBLE_INDIRECT_FILTERS
        )
        query = apply_direct_filters(query, direct_filters)
        query = apply_indirect_filters(query, indirect_filters)
    # pagination
    query, total_count = apply_pagination(query, page, page_limit)

    # get final data
    final_data = get_final_data(query)

    # add service objects
    final_data = add_service_objects(final_data)

    # add pagination data
    response = add_pagination_data(
        response, page, total_count, page_limit, final_data, pagination_data_required
    )

    return response
