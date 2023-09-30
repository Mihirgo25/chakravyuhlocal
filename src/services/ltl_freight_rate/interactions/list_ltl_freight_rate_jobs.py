from services.ltl_freight_rate.models.ltl_freight_rate_jobs import LtlFreightRateJob
from services.ltl_freight_rate.models.ltl_freight_rate_job_mappings import (
    LtlFreightRateJobMapping,
)
from services.ltl_freight_rate.helpers.generate_csv_file_url_for_ltl import (
    generate_csv_file_url_for_ltl,
)
import json
from libs.get_applicable_filters import get_applicable_filters
from libs.get_filters import get_filters
from datetime import datetime, timedelta


possible_direct_filters = [
    "origin_location_id",
    "destination_location_id",
    "commodity_type",
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
    "commodity_type",
    "created_at",
    "updated_at",
    "status",
    "service_provider",
    "service_provider_id",
    "origin_location",
    "origin_location_id",
    "destination_location",
    "destination_location_id",
    "serial_id",
    "sources",
]


def list_ltl_freight_rate_jobs(
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
        return generate_csv_file_url_for_ltl(query)

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
        source_id = LtlFreightRateJobMapping.select(LtlFreightRateJobMapping.source_id).where(LtlFreightRateJobMapping.job_id == d['id']).first()
        d['source_id'] = source_id.source_id
    return list(query.dicts())


def includes_filter(includes):
    if includes:
        ltl_all_fields = list(LtlFreightRateJob._meta.fields.keys())
        required_ltl_fields = [a for a in includes.keys() if a in ltl_all_fields]
        ltl_fields = [getattr(LtlFreightRateJob, key) for key in required_ltl_fields]
    else:
        ltl_fields = [
            getattr(LtlFreightRateJob, key) for key in DEFAULT_REQUIRED_FIELDS
        ]
    query = LtlFreightRateJob.select(*ltl_fields)
    return query


def sort_query(sort_by, sort_type, query):
    if sort_by:
        query = query.order_by(
            eval("LtlFreightRateJob.{}.{}()".format(sort_by, sort_type))
        )
    return query


def apply_indirect_filters(query, filters):
    for key in filters:
        apply_filter_function = f"apply_{key}_filter"
        query = eval(f"{apply_filter_function}(query, filters)")
    return query


def apply_updated_at_filter(query, filters):
    query = query.where(LtlFreightRateJob.updated_at > filters["updated_at"])
    return query


def apply_source_filter(query, filters):
    query = query.where(LtlFreightRateJob.sources.contains(filters["source"]))
    return query


def apply_start_date_filter(query, filters):
    start_date = filters.get("start_date")
    if start_date:
        start_date = datetime.strptime(start_date, STRING_FORMAT) + timedelta(
            hours=5, minutes=30
        )
    query = query.where(LtlFreightRateJob.created_at.cast("date") >= start_date.date())
    return query


def apply_end_date_filter(query, filters):
    end_date = filters.get("end_date")
    if end_date:
        end_date = datetime.strptime(end_date, STRING_FORMAT) + timedelta(
            hours=5, minutes=30
        )
        query = query.where(
            LtlFreightRateJob.created_at.cast("date") <= end_date.date()
        )
    return query


def apply_filters(query, filters):
    direct_filters, indirect_filters = get_applicable_filters(
        filters, possible_direct_filters, possible_indirect_filters
    )
    # applying direct filters
    query = get_filters(direct_filters, query, LtlFreightRateJob)

    # applying indirect filters
    query = apply_indirect_filters(query, indirect_filters)
    
    query = apply_is_visible_filter(query)

    return query


def apply_status_filters(query, filters):
    query = query.join(
        LtlFreightRateJobMapping,
        on=(LtlFreightRateJobMapping.job_id == LtlFreightRateJob.id),
    ).where(LtlFreightRateJobMapping.status == filters.get("status"))
    return query

def apply_is_visible_filter(query):
    query = query.where(LtlFreightRateJob.is_visible == True)
    return query