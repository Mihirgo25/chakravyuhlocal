from playhouse.postgres_ext import SQL
import json, uuid, math
from libs.get_filters import get_filters

from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
from services.haulage_freight_rate.models.haulage_freight_rate_audit import HaulageFreightRateAudit
from playhouse.shortcuts import model_to_dict

import services.haulage_freight_rate.interactions.list_haulage_freight_rates as list_haulage_freight_rate

from libs.get_applicable_filters import get_applicable_filters
from fastapi.encoders import jsonable_encoder


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
]

POSSIBLE_INDIRECT_FILTERS = [
    "origin_location_ids",
    "destination_location_ids",
    "transport_modes",
    "is_rate_available",
    "procured_by_id",
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


def list_haulage_freight_rates(
    filters={}, page_limit=10, page=1, return_query=True, pagination_data_required=True
):
    query = get_query()
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        direct_filters, indirect_filters = get_applicable_filters(
            filters, POSSIBLE_DIRECT_FILTERS, POSSIBLE_INDIRECT_FILTERS
        )
        query = apply_direct_filters(query, direct_filters)

        query = apply_indirect_filters(query, indirect_filters)
    if return_query:
        return {"list": query}

    data = get_data(query)

    return data


def get_query():
    query = HaulageFreightRate.select(
    )
    return query


def get_data(query):
    raw_data = jsonable_encoder(list(query.dicts()))
    ids = [id["id"] for id in raw_data]
    rate_audits = HaulageFreightRateAudit.select().where(
        HaulageFreightRateAudit.object_id << ids,
        HaulageFreightRateAudit.object_type == "HaulageFreightRate",
    )
    for result in raw_data:
        rate_audit = (
            rate_audits.where(HaulageFreightRateAudit.object_id == result["id"])
            .order_by(SQL("updated_at desc"))
        )
        rate_audit = list(rate_audit.dicts())[0]
        result["sourced_by_id"] = rate_audit["sourced_by_id"]
        result["procured_by_id"] = rate_audit["procured_by_id"]

    return raw_data



def apply_is_rate_available_filter(query, val, filters):
    query = query.where(HaulageFreightRate.rate_not_available_entry != True)
    return query


def apply_transport_modes_filter(query, val, filters):
    transport_modes = filters["transport_modes"]
    query = query.where(HaulageFreightRate.transport_modes.contains(transport_modes))
    # query.where('haulage_freight_rates.transport_modes && ?', "{#{transport_modes.join(',')}}")
    return query
