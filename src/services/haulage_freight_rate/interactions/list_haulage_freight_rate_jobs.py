from services.haulage_freight_rate.models.haulage_freight_rate_jobs import HaulageFreightRateJob
from services.haulage_freight_rate.models.haulage_freight_rate_job_mappings import HaulageFreightRateJobMapping
from services.haulage_freight_rate.helpers.generate_csv_file_url_for_haulage import (
    generate_csv_file_url_for_haulage,
)
import json, math
from libs.get_applicable_filters import get_applicable_filters
from libs.get_filters import get_filters
from datetime import datetime, timedelta
from functools import reduce


possible_direct_filters = [
    "origin_location_id",
    "destination_location_id",
    "shipping_line_id",
    "commodity",
    "user_id",
    "serial_id",
    "status",
    "cogo_entity_id",
    "service_provider_id",
    "transport_modes_keyword"
]
possible_indirect_filters = ["updated_at", "source", "is_flash_booking_reverted", "source_id", "shipment_serial_id"]


STRING_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"


DEFAULT_REQUIRED_FIELDS = [
    "id",
    "assigned_to",
    "closed_by",
    "closed_by_id",
    "closing_remarks",
    "commodity",
    "container_size",
    "created_at",
    "updated_at",
    "status",
    "shipping_line",
    "shipping_line_id",
    "service_provider",
    "service_provider_id",
    "haulage_type",
    "trailer_type",
    "trip_type",
    "rate_type",
    "origin_location",
    "origin_location_id",
    "destination_location",
    "destination_location_id",
    "serial_id",
    "container_type",
    "transport_modes_keyword",
    "sources",
]


def list_haulage_freight_rate_jobs(
    filters={},
    page_limit=10,
    page=1,
    sort_by="updated_at",
    sort_type="desc",
    generate_csv_url=False,
    pagination_data_required=False,
    includes={},
):
    response = {"success": False, "status_code": 200}
    
    query = includes_filter(includes)

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        query = apply_filters(query, filters)


    if generate_csv_url:
        return generate_csv_file_url_for_haulage(query)
    
    total_count = query.count() if pagination_data_required else None

    if page_limit:
        query = query.paginate(page, page_limit)

    query = sort_query(sort_by, sort_type, query)

    data = get_data(query, filters)

    response = add_pagination_data(
        response, page, page_limit, data, pagination_data_required, total_count
    )

    return response


def get_data(query, filters):
    data = list(query.dicts())
    for d in data:
        mappings_query = HaulageFreightRateJobMapping.select(HaulageFreightRateJobMapping.shipment_serial_id, HaulageFreightRateJobMapping.source_id, HaulageFreightRateJobMapping.shipment_id, HaulageFreightRateJobMapping.status).where(HaulageFreightRateJobMapping.job_id == d['id'])
        if filters and filters.get('source'):
            if not isinstance(filters.get('source'), list):
                filters['source'] = [filters.get('source')]
            mappings_query = mappings_query.where(HaulageFreightRateJobMapping.source << filters.get('source'))
        mappings_data = mappings_query.first()
        if mappings_data:
            d['source_id'] = mappings_data.source_id
            d['shipment_id'] = mappings_data.shipment_id
            d['reverted_status'] = mappings_data.status
            d['shipment_serial_id'] = mappings_data.shipment_serial_id
    return data


def includes_filter(includes):
    if includes:
        haulage_all_fields = list(HaulageFreightRateJob._meta.fields.keys())
        required_haulage_fields = [a for a in includes.keys() if a in haulage_all_fields]
        haulage_fields = [getattr(HaulageFreightRateJob, key) for key in required_haulage_fields]
    else:
        haulage_fields = [
            getattr(HaulageFreightRateJob, key) for key in DEFAULT_REQUIRED_FIELDS
        ]
    query = HaulageFreightRateJob.select(*haulage_fields)
    return query


def sort_query(sort_by, sort_type, query):
    if sort_by:
        query = query.order_by(
            eval("HaulageFreightRateJob.{}.{}()".format(sort_by, sort_type))
        )
    return query


def apply_indirect_filters(query, filters):
    for key in filters:
        apply_filter_function = f"apply_{key}_filter"
        query = eval(f"{apply_filter_function}(query, filters)")
    return query


def apply_updated_at_filter(query, filters):
    query = query.where(HaulageFreightRateJob.updated_at > filters["updated_at"])
    return query


def apply_source_filter(query, filters):
    if filters.get('source') and not isinstance(filters.get('source'), list):
        filters['source'] = [filters.get('source')]
    conditions = [HaulageFreightRateJob.sources.contains(tag) for tag in filters["source"]]
    combined_condition = reduce(lambda a, b: a | b, conditions)
    query = query.where(combined_condition)
    return query


def apply_start_date_filter(query, filters):
    start_date = datetime.strptime(filters["start_date"], STRING_FORMAT) + timedelta(
        hours=5, minutes=30
    )
    query = query.where(HaulageFreightRateJob.created_at.cast("date") >= start_date.date())
    return query


def apply_source_id_filter(query, filters):
    if filters.get('source_id') and not isinstance(filters.get('source_id'), list):
        filters['source_id'] = [filters.get('source_id')]
    subquery = list(HaulageFreightRateJobMapping.select(HaulageFreightRateJobMapping.job_id).where(HaulageFreightRateJobMapping.source_id << filters['source_id']).dicts())
    job_ids = []
    for data in subquery:
        job_ids.append(data['job_id'])
    query = query.where(HaulageFreightRateJob.id << job_ids)
    return query

def apply_shipment_serial_id_filter(query, filters):
    if filters.get('shipment_serial_id') and not isinstance(filters.get('shipment_serial_id'), list):
        filters['shipment_serial_id'] = [filters.get('shipment_serial_id')]
    subquery = list(HaulageFreightRateJobMapping.select(HaulageFreightRateJobMapping.job_id).where(HaulageFreightRateJobMapping.shipment_serial_id << filters['shipment_serial_id']).dicts())
    job_ids = []
    for data in subquery:
        job_ids.append(data['job_id'])
    query = query.where(HaulageFreightRateJob.id << job_ids)
    return query

def apply_end_date_filter(query, filters):
    end_date = datetime.strptime(filters["start_date"], STRING_FORMAT) + timedelta(
        hours=5, minutes=30
    )
    query = query.where(HaulageFreightRateJob.created_at.cast("date") <= end_date.date())
    return query


def apply_filters(query, filters):
    direct_filters, indirect_filters = get_applicable_filters(
        filters, possible_direct_filters, possible_indirect_filters
    )
    # applying direct filters
    query = get_filters(direct_filters, query, HaulageFreightRateJob)

    # applying indirect filters
    query = apply_indirect_filters(query, indirect_filters)
    
    query = apply_is_visible_filter(query)

    return query

def apply_is_visible_filter(query):
    query = query.where(HaulageFreightRateJob.is_visible == True)
    return query

def apply_is_flash_booking_reverted_filter(query, filters):
    if filters.get('is_flash_booking_reverted'):
        query = query.join(HaulageFreightRateJobMapping, on=(HaulageFreightRateJobMapping.job_id == HaulageFreightRateJob.id)).where(HaulageFreightRateJobMapping.status == 'reverted')
    else:
        query = query.join(HaulageFreightRateJobMapping, on=(HaulageFreightRateJobMapping.job_id == HaulageFreightRateJob.id)).where(HaulageFreightRateJobMapping.status != 'reverted')
    return query

def add_pagination_data(
    response, page, page_limit, final_data, pagination_data_required, total_count
):
    if pagination_data_required:
        response["page"] = page
        response["total"] = math.ceil(total_count / page_limit)
        response["total_count"] = total_count
        response["page_limit"] = page_limit
    response["success"] = True
    response["list"] = final_data
    return response