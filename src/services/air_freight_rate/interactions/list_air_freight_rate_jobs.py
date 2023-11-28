from services.air_freight_rate.models.air_freight_rate_jobs import AirFreightRateJob
from services.air_freight_rate.models.air_freight_rate_jobs_mapping import AirFreightRateJobMapping
from services.air_freight_rate.helpers.generate_csv_file_url_for_air import (
    generate_csv_file_url_for_air,
)
import json, math
from libs.get_applicable_filters import get_applicable_filters
from libs.get_filters import get_filters
from libs.json_encoder import json_encoder
from datetime import datetime, timedelta
from peewee import fn
from playhouse.postgres_ext import SQL, Case
from functools import reduce


possible_direct_filters = [
    "origin_airport_id",
    "destination_airport_id",
    "airline_id",
    "commodity",
    "user_id",
    "serial_id",
    "status",
    "cogo_entity_id",
    "service_provider_id",
]
possible_indirect_filters = ["updated_at", "start_date", "end_date", "source", "is_flash_booking_reverted", "source_id", "source_serial_id"]


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
    pagination_data_required=False,
    includes={},
):
    response = {"success": False, "status_code": 200}
    
    query = includes_filters(includes)

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        query = apply_filters(query, filters)


    if generate_csv_url:
        return generate_csv_file_url_for_air(query)
    
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
        mappings_query = AirFreightRateJobMapping.select(AirFreightRateJobMapping.shipment_service_id ,AirFreightRateJobMapping.source_serial_id, AirFreightRateJobMapping.source_id, AirFreightRateJobMapping.shipment_id, AirFreightRateJobMapping.status).where(AirFreightRateJobMapping.job_id == d['id'])
        if filters and filters.get('source'):
            if not isinstance(filters.get('source'), list):
                filters['source'] = [filters.get('source')]
            mappings_query = mappings_query.where(AirFreightRateJobMapping.source << filters.get('source'))
        mappings_data = mappings_query.first()
        if mappings_data:
            d['source_id'] = mappings_data.source_id
            d['shipment_id'] = mappings_data.shipment_id
            d['reverted_status'] = mappings_data.status
            d['source_serial_id'] = mappings_data.source_serial_id
            d['shipment_service_id'] = mappings_data.shipment_service_id
            d['reverted_count'] = get_reverted_count(mappings_data)
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
    if filters.get('source') and not isinstance(filters.get('source'), list):
        filters['source'] = [filters.get('source')]
    conditions = [AirFreightRateJob.sources.contains(tag) for tag in filters["source"]]
    combined_condition = reduce(lambda a, b: a | b, conditions)
    query = query.where(combined_condition)
    return query


def apply_start_date_filter(query, filters):
    start_date = filters.get("start_date")
    if start_date:
        start_date = datetime.strptime(start_date, STRING_FORMAT) + timedelta(
            hours=5, minutes=30
        )
        query = query.where(AirFreightRateJob.updated_at.cast("date") >= start_date.date())
    return query


def apply_source_id_filter(query, filters):
    if filters.get('source_id') and not isinstance(filters.get('source_id'), list):
        filters['source_id'] = [filters.get('source_id')]
    subquery = list(AirFreightRateJobMapping.select(AirFreightRateJobMapping.job_id).where(AirFreightRateJobMapping.source_id << filters['source_id']).dicts())
    job_ids = []
    for data in subquery:
        job_ids.append(data['job_id'])
    query = query.where(AirFreightRateJob.id << job_ids)
    return query

def apply_source_serial_id_filter(query, filters):
    if filters.get('source_serial_id') and not isinstance(filters.get('source_serial_id'), list):
        filters['source_serial_id'] = [filters.get('source_serial_id')]
    subquery = list(AirFreightRateJobMapping.select(AirFreightRateJobMapping.job_id).where(AirFreightRateJobMapping.source_serial_id << filters['source_serial_id']).dicts())
    job_ids = []
    for data in subquery:
        job_ids.append(data['job_id'])
    query = query.where(AirFreightRateJob.id << job_ids)
    return query

def apply_end_date_filter(query, filters):
    end_date = filters.get("end_date")
    if end_date:
        end_date = datetime.strptime(end_date, STRING_FORMAT) + timedelta(
            hours=5, minutes=30
        )
        query = query.where(AirFreightRateJob.updated_at.cast("date") <= end_date.date())
    return query


def apply_filters(query, filters):
    direct_filters, indirect_filters = get_applicable_filters(
        filters, possible_direct_filters, possible_indirect_filters
    )
    # applying direct filters
    query = get_filters(direct_filters, query, AirFreightRateJob)

    # applying indirect filters
    query = apply_indirect_filters(query, indirect_filters)
    
    # query = apply_is_visible_filter(query)

    return query

def apply_is_flash_booking_reverted_filter(query, filters):
    if filters.get('is_flash_booking_reverted'):
        query = query.join(AirFreightRateJobMapping, on=(AirFreightRateJobMapping.job_id == AirFreightRateJob.id)).where(AirFreightRateJobMapping.status == 'reverted')
    else:
        query = query.join(AirFreightRateJobMapping, on=(AirFreightRateJobMapping.job_id == AirFreightRateJob.id)).where(AirFreightRateJobMapping.status != 'reverted')
    return query

def apply_is_visible_filter(query):
    query = query.where(AirFreightRateJob.is_visible == True)
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
        result = AirFreightRateJobMapping.select(AirFreightRateJobMapping.id).where(
                    (AirFreightRateJobMapping.shipment_id == mappings_data.shipment_id) &
                    (AirFreightRateJobMapping.status == 'reverted')
                ).count()
        return result
    return None
