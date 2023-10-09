from services.air_freight_rate.models.air_freight_rate_jobs import AirFreightRateJob
from services.air_freight_rate.models.air_freight_rate_jobs_mapping import AirFreightRateJobMapping
from services.air_freight_rate.helpers.generate_csv_file_url_for_air import (
    generate_csv_file_url_for_air,
)
import json
from libs.get_applicable_filters import get_applicable_filters
from libs.get_filters import get_filters
from libs.json_encoder import json_encoder
from datetime import datetime, timedelta
from peewee import fn
from playhouse.postgres_ext import SQL, Case


possible_direct_filters = [
    "origin_airport_id",
    "destination_airport_id",
    "airline_id",
    "commodity",
    "user_id",
    "serial_id",
    "status",
    "cogo_entity_id"
]
possible_indirect_filters = ["updated_at", "start_date", "end_date", "source"]


STRING_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


DEFAULT_REQUIRED_FIELDS = [
    "id",
    "assigned_to",
    "closed_by",
    "closing_remarks",
    "commodity",
    "created_at",
    "updated_at",
    "status",
    "airline",
    "airline_id",
    "service_provider",
    "service_provider_id",
    "origin_airport",
    "origin_airport_id",
    "destination_airport",
    "destination_airport_id",
    "shipment_type",
    "stacking_type",
    "commodity_type",
    "commodity_sub_type",
    "operation_type",
    "stacking_type",
    "serial_id",
    "price_type",
    "sources",

]


def list_air_freight_rate_jobs(
    filters={},
    page_limit=10,
    page=1,
    sort_by="updated_at",
    sort_type="desc",
    generate_csv_url=False,
    includes={},
):
    query = includes_filters(includes)

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        query = apply_filters(query, filters)


    if generate_csv_url:
        return generate_csv_file_url_for_air(query)
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
        mappings_data = AirFreightRateJobMapping.select(AirFreightRateJobMapping.source_id, AirFreightRateJobMapping.shipment_id).where(AirFreightRateJobMapping.job_id == d['id']).first()
        if mappings_data:
            d['source_id'] = mappings_data.source_id
            d['shipment_id'] = mappings_data.shipment_id
            d['reverted_status'] = mappings_data.status
    return data


def includes_filters(includes):
    if includes:
        fcl_all_fields = list(AirFreightRateJob._meta.fields.keys())
        required_fcl_fields = [a for a in includes.keys() if a in fcl_all_fields]
        air_fields = [getattr(AirFreightRateJob, key) for key in required_fcl_fields]
    else:
        air_fields = [
            getattr(AirFreightRateJob, key) for key in DEFAULT_REQUIRED_FIELDS
        ]
    query = AirFreightRateJob.select(*air_fields)
    return query


def sort_query(sort_by, sort_type, query):
    if sort_by:
        query = query.order_by(
            eval("AirFreightRateJob.{}.{}()".format(sort_by, sort_type))
        )
    return query


def apply_indirect_filters(query, filters):
    for key in filters:
        apply_filter_function = f"apply_{key}_filter"
        query = eval(f"{apply_filter_function}(query, filters)")
    return query


def apply_updated_at_filter(query, filters):
    query = query.where(AirFreightRateJob.updated_at > filters["updated_at"])
    return query


def apply_source_filter(query, filters):
    query = query.where(AirFreightRateJob.sources.contains(filters["source"]))
    return query


def apply_start_date_filter(query, filters):
    start_date = filters.get("start_date")
    if start_date:
        start_date = datetime.strptime(start_date, STRING_FORMAT) + timedelta(
            hours=5, minutes=30
        )
        query = query.where(AirFreightRateJob.created_at.cast("date") >= start_date.date())
    return query


def apply_end_date_filter(query, filters):
    end_date = filters.get("end_date")
    if end_date:
        end_date = datetime.strptime(end_date, STRING_FORMAT) + timedelta(
            hours=5, minutes=30
        )
        query = query.where(AirFreightRateJob.created_at.cast("date") <= end_date.date())
    return query


def apply_filters(query, filters):
    direct_filters, indirect_filters = get_applicable_filters(
        filters, possible_direct_filters, possible_indirect_filters
    )
    # applying direct filters
    query = get_filters(direct_filters, query, AirFreightRateJob)

    # applying indirect filters
    query = apply_indirect_filters(query, indirect_filters)
    
    query = apply_is_visible_filter(query)

    return query

def apply_is_visible_filter(query):
    query = query.where(AirFreightRateJob.is_visible == True)
    return query
