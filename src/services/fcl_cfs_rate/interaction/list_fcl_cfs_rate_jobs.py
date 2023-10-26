from services.fcl_cfs_rate.models.fcl_cfs_rate_jobs import FclCfsRateJob
from services.fcl_cfs_rate.models.fcl_cfs_rate_job_mappings import (
    FclCfsRateJobMapping,
)
from services.fcl_cfs_rate.helpers.generate_csv_file_url_for_fcl_cfs import (
    generate_csv_file_url_for_fcl_cfs,
)
import json, math
from libs.get_applicable_filters import get_applicable_filters
from libs.get_filters import get_filters
from datetime import datetime, timedelta
from functools import reduce


possible_direct_filters = [
    "location_id",
    "service_provider_id",
    "commodity",
    "user_id",
    "serial_id",
    "status",
    "cogo_entity_id"
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
    "trade_type",
    "service_provider",
    "service_provider_id",
    "cargo_handling_type",
    "location_id",
    "location",
    "serial_id",
    "container_type",
    "rate_type",
    "sources",
]


def list_fcl_cfs_rate_jobs(
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
        return generate_csv_file_url_for_fcl_cfs(query)
    
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
        mappings_query = FclCfsRateJobMapping.select(FclCfsRateJobMapping.shipment_service_id, FclCfsRateJobMapping.shipment_serial_id, FclCfsRateJobMapping.source_id, FclCfsRateJobMapping.shipment_id, FclCfsRateJobMapping.status).where(FclCfsRateJobMapping.job_id == d['id'])
        if filters and filters.get('source'):
            if not isinstance(filters.get('source'), list):
                filters['source'] = [filters.get('source')]
            mappings_query = mappings_query.where(FclCfsRateJobMapping.source << filters.get('source'))
        mappings_data = mappings_query.first()
        if mappings_data:
            d['source_id'] = mappings_data.source_id
            d['shipment_id'] = mappings_data.shipment_id
            d['reverted_status'] = mappings_data.status
            d['shipment_serial_id'] = mappings_data.shipment_serial_id
            d['shipment_service_id'] = mappings_data.shipment_service_id
            d['reverted_count'] = get_reverted_count(mappings_data)
    return data


def includes_filter(includes):
    if includes:
        fcl_all_fields = list(FclCfsRateJob._meta.fields.keys())
        required_fcl_fields = [a for a in includes.keys() if a in fcl_all_fields]
        fcl_fields = [getattr(FclCfsRateJob, key) for key in required_fcl_fields]
    else:
        fcl_fields = [
            getattr(FclCfsRateJob, key) for key in DEFAULT_REQUIRED_FIELDS
        ]
    query = FclCfsRateJob.select(*fcl_fields)
    return query


def sort_query(sort_by, sort_type, query):
    if sort_by:
        query = query.order_by(
            eval("FclCfsRateJob.{}.{}()".format(sort_by, sort_type))
        )
    return query


def apply_indirect_filters(query, filters):
    for key in filters:
        apply_filter_function = f"apply_{key}_filter"
        query = eval(f"{apply_filter_function}(query, filters)")
    return query


def apply_updated_at_filter(query, filters):
    query = query.where(FclCfsRateJob.updated_at > filters["updated_at"])
    return query


def apply_source_filter(query, filters):
    if filters.get('source') and not isinstance(filters.get('source'), list):
        filters['source'] = [filters.get('source')]
    conditions = [FclCfsRateJob.sources.contains(tag) for tag in filters["source"]]
    combined_condition = reduce(lambda a, b: a | b, conditions)
    query = query.where(combined_condition)
    return query


def apply_start_date_filter(query, filters):
    start_date = filters.get("start_date")
    if start_date:
        start_date = datetime.strptime(start_date, STRING_FORMAT) + timedelta(
            hours=5, minutes=30
        )
    query = query.where(FclCfsRateJob.created_at.cast("date") >= start_date.date())
    return query


def apply_source_id_filter(query, filters):
    if filters.get('source_id') and not isinstance(filters.get('source_id'), list):
        filters['source_id'] = [filters.get('source_id')]
    subquery = list(FclCfsRateJobMapping.select(FclCfsRateJobMapping.job_id).where(FclCfsRateJobMapping.source_id << filters['source_id']).dicts())
    job_ids = []
    for data in subquery:
        job_ids.append(data['job_id'])
    query = query.where(FclCfsRateJob.id << job_ids)
    return query

def apply_shipment_serial_id_filter(query, filters):
    if filters.get('shipment_serial_id') and not isinstance(filters.get('shipment_serial_id'), list):
        filters['shipment_serial_id'] = [filters.get('shipment_serial_id')]
    subquery = list(FclCfsRateJobMapping.select(FclCfsRateJobMapping.job_id).where(FclCfsRateJobMapping.shipment_serial_id << filters['shipment_serial_id']).dicts())
    job_ids = []
    for data in subquery:
        job_ids.append(data['job_id'])
    query = query.where(FclCfsRateJob.id << job_ids)
    return query

def apply_end_date_filter(query, filters):
    end_date = filters.get("end_date")
    if end_date:
        end_date = datetime.strptime(end_date, STRING_FORMAT) + timedelta(
            hours=5, minutes=30
        )
        query = query.where(
            FclCfsRateJob.created_at.cast("date") <= end_date.date()
        )
    return query


def apply_filters(query, filters):
    direct_filters, indirect_filters = get_applicable_filters(
        filters, possible_direct_filters, possible_indirect_filters
    )
    # applying direct filters
    query = get_filters(direct_filters, query, FclCfsRateJob)

    # applying indirect filters
    query = apply_indirect_filters(query, indirect_filters)

    query = apply_is_visible_filter(query)

    return query


def apply_is_visible_filter(query):
    query = query.where(FclCfsRateJob.is_visible == True)
    return query

def apply_is_flash_booking_reverted_filter(query, filters):
    if filters.get('is_flash_booking_reverted'):
        query = query.join(FclCfsRateJobMapping, on=(FclCfsRateJobMapping.job_id == FclCfsRateJob.id)).where(FclCfsRateJobMapping.status == 'reverted')
    else:
        query = query.join(FclCfsRateJobMapping, on=(FclCfsRateJobMapping.job_id == FclCfsRateJob.id)).where(FclCfsRateJobMapping.status != 'reverted')
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

def get_reverted_count(mappings_data):
    if mappings_data.shipment_id:
        result = FclCfsRateJobMapping.select(FclCfsRateJobMapping.id).where(
                    (FclCfsRateJobMapping.shipment_id == mappings_data.shipment_id) &
                    (FclCfsRateJobMapping.status == 'reverted')
                ).count()
        return result
    return None