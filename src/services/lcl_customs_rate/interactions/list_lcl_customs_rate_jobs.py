from services.lcl_customs_rate.models.lcl_customs_rate_jobs import LclCustomsRateJob
from services.lcl_customs_rate.models.lcl_customs_rate_job_mappings import (
    LclCustomsRateJobMapping,
)
from services.lcl_customs_rate.helpers.generate_csv_file_url_for_lcl_customs import generate_csv_file_url_for_lcl_customs
import json
from libs.get_applicable_filters import get_applicable_filters
from libs.get_filters import get_filters
from datetime import datetime, timedelta


possible_direct_filters = ["location_id", "commodity", "user_id", "serial_id", "status", "cogo_entity_id"]
possible_indirect_filters = ["updated_at", "start_date", "end_date", "source"]


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
    "service_provider",
    "service_provider_id",
    "importer_exporter",
    "importer_exporter_id",
    "location",
    "location_id",
    "serial_id",
    "container_type",
    "sources",
]


def list_lcl_customs_rate_jobs(
    filters={},
    page_limit=10,
    page=1,
    sort_by="updated_at",
    sort_type="desc",
    generate_csv_url=False,
    includes={},
):
    query = includes_filter(includes)

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        query = apply_filters(query, filters)

    if generate_csv_url:
        return generate_csv_file_url_for_lcl_customs(query)

    if page_limit:
        query = query.paginate(page, page_limit)

    query = sort_query(sort_by, sort_type, query)

    data = get_data(query, filters)

    return {
        "list": data,
    }


def get_data(query, filters):
    data = list(query.dicts())
    for d in data:
        mappings_query = LclCustomsRateJobMapping.select(LclCustomsRateJobMapping.source_id, LclCustomsRateJobMapping.shipment_id).where(LclCustomsRateJobMapping.job_id == d['id'])
        if filters and filters.get('source'):
            mappings_query = mappings_query.where(LclCustomsRateJobMapping.source == filters.get('source'))
        mappings_data = mappings_query.first()
        if mappings_data:
            d['source_id'] = mappings_data.source_id
            d['shipment_id'] = mappings_data.shipment_id
            d['reverted_status'] = mappings_data.status
    return data



def includes_filter(includes):
    if includes:
        lcl_all_fields = list(LclCustomsRateJob._meta.fields.keys())
        required_lcl_fields = [a for a in includes.keys() if a in lcl_all_fields]
        lcl_fields = [getattr(LclCustomsRateJob, key) for key in required_lcl_fields]
    else:
        lcl_fields = [
            getattr(LclCustomsRateJob, key) for key in DEFAULT_REQUIRED_FIELDS
        ]
    query = LclCustomsRateJob.select(*lcl_fields)
    return query


def sort_query(sort_by, sort_type, query):
    if sort_by:
        query = query.order_by(
            eval("LclCustomsRateJob.{}.{}()".format(sort_by, sort_type))
        )
    return query


def apply_indirect_filters(query, filters):
    for key in filters:
        apply_filter_function = f"apply_{key}_filter"
        query = eval(f"{apply_filter_function}(query, filters)")
    return query


def apply_updated_at_filter(query, filters):
    query = query.where(LclCustomsRateJob.updated_at > filters["updated_at"])
    return query


def apply_source_filter(query, filters):
    query = query.where(LclCustomsRateJob.sources.contains(filters["source"]))
    return query


def apply_start_date_filter(query, filters):
    start_date = datetime.strptime(filters["start_date"], STRING_FORMAT) + timedelta(
        hours=5, minutes=30
    )
    query = query.where(LclCustomsRateJob.created_at.cast("date") >= start_date.date())
    return query


def apply_end_date_filter(query, filters):
    end_date = datetime.strptime(filters["start_date"], STRING_FORMAT) + timedelta(
        hours=5, minutes=30
    )
    query = query.where(LclCustomsRateJob.created_at.cast("date") <= end_date.date())
    return query


def apply_filters(query, filters):
    direct_filters, indirect_filters = get_applicable_filters(
        filters, possible_direct_filters, possible_indirect_filters
    )
    # applying direct filters
    query = get_filters(direct_filters, query, LclCustomsRateJob)

    # applying indirect filters
    query = apply_indirect_filters(query, indirect_filters)

    query = apply_is_visible_filter(query)

    return query


def apply_is_visible_filter(query):
    query = query.where(LclCustomsRateJob.is_visible == True)
    return query
