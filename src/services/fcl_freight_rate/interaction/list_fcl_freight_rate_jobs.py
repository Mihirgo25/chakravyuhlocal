from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJob
from services.fcl_freight_rate.models.fcl_freight_rate_job_mappings import (
    FclFreightRateJobMapping,
)
from services.fcl_freight_rate.helpers.generate_csv_file_url_for_fcl import (
    generate_csv_file_url_for_fcl,
)
import json
from libs.get_applicable_filters import get_applicable_filters
from libs.get_filters import get_filters
from datetime import datetime, timedelta


possible_direct_filters = [
    "origin_port_id",
    "destination_port_id",
    "shipping_line_id",
    "commodity",
    "user_id",
    "serial_id",
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
    "container_size",
    "created_at",
    "updated_at",
    "status",
    "shipping_line",
    "shipping_line_id",
    "service_provider",
    "service_provider_id",
    "origin_port",
    "origin_port_id",
    "destination_port",
    "destination_port_id",
    "serial_id",
    "container_type",
    "sources",
    "origin_main_port_id",
    "destination_main_port_id",
]


def list_fcl_freight_rate_jobs(
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
        return generate_csv_file_url_for_fcl(query)

    if page_limit:
        query = query.paginate(page, page_limit)

    query = sort_query(sort_by, sort_type, query)
    data = get_data(query)

    return {
        "list": data,
    }


def get_data(query):
    data = list(query.dicts())
    for d in data:
        source_id = FclFreightRateJobMapping.select(FclFreightRateJobMapping.source_id).where(FclFreightRateJobMapping.job_id == d['id']).first()
        d['source_id'] = source_id.source_id
    return data


def includes_filter(includes):
    if includes:
        fcl_all_fields = list(FclFreightRateJob._meta.fields.keys())
        required_fcl_fields = [a for a in includes.keys() if a in fcl_all_fields]
        fcl_fields = [getattr(FclFreightRateJob, key) for key in required_fcl_fields]
    else:
        fcl_fields = [
            getattr(FclFreightRateJob, key) for key in DEFAULT_REQUIRED_FIELDS
        ]
    query = FclFreightRateJob.select(*fcl_fields)
    return query


def sort_query(sort_by, sort_type, query):
    if sort_by:
        query = query.order_by(
            eval("FclFreightRateJob.{}.{}()".format(sort_by, sort_type))
        )
    return query


def apply_indirect_filters(query, filters):
    for key in filters:
        apply_filter_function = f"apply_{key}_filter"
        query = eval(f"{apply_filter_function}(query, filters)")
    return query


def apply_updated_at_filter(query, filters):
    query = query.where(FclFreightRateJob.updated_at > filters["updated_at"])
    return query


def apply_source_filter(query, filters):
    query = query.where(FclFreightRateJob.sources.contains(filters["source"]))
    return query


def apply_start_date_filter(query, filters):
    start_date = filters.get("start_date")
    if start_date:
        start_date = datetime.strptime(start_date, STRING_FORMAT) + timedelta(
            hours=5, minutes=30
        )
    query = query.where(FclFreightRateJob.created_at.cast("date") >= start_date.date())
    return query


def apply_end_date_filter(query, filters):
    end_date = filters.get("end_date")
    if end_date:
        end_date = datetime.strptime(end_date, STRING_FORMAT) + timedelta(
            hours=5, minutes=30
        )
        query = query.where(
            FclFreightRateJob.created_at.cast("date") <= end_date.date()
        )
    return query


def apply_filters(query, filters):
    direct_filters, indirect_filters = get_applicable_filters(
        filters, possible_direct_filters, possible_indirect_filters
    )
    # applying direct filters
    query = get_filters(direct_filters, query, FclFreightRateJob)

    # applying indirect filters
    query = apply_indirect_filters(query, indirect_filters)

    query = apply_is_visible_filter(query)

    return query


def apply_status_filters(query, filters):
    query = query.join(
        FclFreightRateJobMapping,
        on=(FclFreightRateJobMapping.job_id == FclFreightRateJob.id),
    ).where(FclFreightRateJobMapping.status == filters.get("status"))
    return query

def apply_is_visible_filter(query):
    query = query.where(FclFreightRateJob.is_visible == True)
