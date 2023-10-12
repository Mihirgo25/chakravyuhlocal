from services.ftl_freight_rate.models.ftl_freight_rate_jobs import FtlFreightRateJob
from services.ftl_freight_rate.models.ftl_freight_rate_job_mappings import FtlFreightRateJobMapping
from services.ftl_freight_rate.helpers.generate_csv_file_url_for_ftl import (
    generate_csv_file_url_for_ftl,
)
import json, math
from libs.get_applicable_filters import get_applicable_filters
from libs.get_filters import get_filters
from datetime import datetime, timedelta


possible_direct_filters = [
    "origin_location_id",
    "destination_location_id",
    "commodity",
    "user_id",
    "serial_id",
    "status",
    "cogo_entity_id"
]
possible_indirect_filters = ["updated_at", "start_date", "end_date", "source"]


STRING_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"


DEFAULT_REQUIRED_FIELDS = [
    "id",
    "assigned_to",
    "closed_by",
    "closed_by_id",
    "closing_remarks",
    "commodity",
    "truck_type",
    "truck_body_type",
    "transit_time",
    "detention_free_time",
    "unit",
    "created_at",
    "updated_at",
    "status",
    "trip_type",
    "service_provider",
    "service_provider_id",
    "origin_location",
    "origin_location_id",
    "destination_location",
    "destination_location_id",
    "rate_type",
    "serial_id",
    "sources",
]


def list_ftl_freight_rate_jobs(
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
        return generate_csv_file_url_for_ftl(query)
    
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
        mappings_query = FtlFreightRateJobMapping.select(FtlFreightRateJobMapping.source_id, FtlFreightRateJobMapping.shipment_id, FtlFreightRateJobMapping.status).where(FtlFreightRateJobMapping.job_id == d['id'])
        if filters and filters.get('source'):
            mappings_query = mappings_query.where(FtlFreightRateJobMapping.source == filters.get('source'))
        mappings_data = mappings_query.first()
        if mappings_data:
            d['source_id'] = mappings_data.source_id
            d['shipment_id'] = mappings_data.shipment_id
            d['reverted_status'] = mappings_data.status
    return data


def includes_filter(includes):
    if includes:
        ftl_all_fields = list(FtlFreightRateJob._meta.fields.keys())
        required_ftl_fields = [a for a in includes.keys() if a in ftl_all_fields]
        ftl_fields = [getattr(FtlFreightRateJob, key) for key in required_ftl_fields]
    else:
        ftl_fields = [
            getattr(FtlFreightRateJob, key) for key in DEFAULT_REQUIRED_FIELDS
        ]
    query = FtlFreightRateJob.select(*ftl_fields)
    return query


def sort_query(sort_by, sort_type, query):
    if sort_by:
        query = query.order_by(
            eval("FtlFreightRateJob.{}.{}()".format(sort_by, sort_type))
        )
    return query


def apply_indirect_filters(query, filters):
    for key in filters:
        apply_filter_function = f"apply_{key}_filter"
        query = eval(f"{apply_filter_function}(query, filters)")
    return query


def apply_updated_at_filter(query, filters):
    query = query.where(FtlFreightRateJob.updated_at > filters["updated_at"])
    return query


def apply_source_filter(query, filters):
    query = query.where(FtlFreightRateJob.sources.contains(filters["source"]))
    return query


def apply_start_date_filter(query, filters):
    start_date = datetime.strptime(filters["start_date"], STRING_FORMAT) + timedelta(
        hours=5, minutes=30
    )
    query = query.where(FtlFreightRateJob.created_at.cast("date") >= start_date.date())
    return query


def apply_end_date_filter(query, filters):
    end_date = datetime.strptime(filters["start_date"], STRING_FORMAT) + timedelta(
        hours=5, minutes=30
    )
    query = query.where(FtlFreightRateJob.created_at.cast("date") <= end_date.date())
    return query


def apply_filters(query, filters):
    direct_filters, indirect_filters = get_applicable_filters(
        filters, possible_direct_filters, possible_indirect_filters
    )
    # applying direct filters
    query = get_filters(direct_filters, query, FtlFreightRateJob)

    # applying indirect filters
    query = apply_indirect_filters(query, indirect_filters)
    
    query = apply_is_visible_filter(query)

    return query

def apply_is_visible_filter(query):
    query = query.where(FtlFreightRateJob.is_visible == True)
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