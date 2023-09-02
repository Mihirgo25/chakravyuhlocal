from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJobs
import json
from libs.get_applicable_filters import get_applicable_filters
from libs.get_filters import get_filters
from libs.json_encoder import json_encoder
from datetime import datetime, timedelta


STRING_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'

possible_direct_filters = [
    "origin_port_id",
    "destination_port_id",
    "shipping_line_id",
    "commodity",
    "status"
]
possible_indirect_filters = ["updated_at", "user_id", "date_range"]

DEFAULT_REQUIRED_FIELDS = [
    'id',
    'assigned_to',
    'closed_by',
    'closing_remarks',
    'commodity',
    'container_size',
    'created_at',
    'updated_at',
    'status',
    'shipping_line',
    'service_provider',
    'origin_port',
    'destination_port',
    'container_type',
]


def list_fcl_freight_rate_coverages(filters = {}, page_limit = 10, page = 1, sort_by = 'updated_at', sort_type = 'desc', generate_csv_url = False, includes = {}):
    query = get_query(sort_by, sort_type, includes)
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)
        direct_filters, indirect_filters = get_applicable_filters(
            filters, possible_direct_filters, possible_indirect_filters
        )
        query = get_filters(direct_filters, query, FclFreightRateJobs)
        query = apply_indirect_filters(query, indirect_filters)
        dynamic_statisitcs, query = get_statisitcs(query, filters)
    if page_limit and not generate_csv_url:
        query = query.paginate(page, page_limit)

    data = get_data(query)

    return {"list": data, "stats": dynamic_statisitcs}


def get_statisitcs(query, filters):
    dynamic_statisitcs = {}
    dynamic_statisitcs['monitoring_dashboard'] = query.where(FclFreightRateJobs.source == 'monitoring_dashboard').count() or 0
    dynamic_statisitcs['spot_search'] = query.where(FclFreightRateJobs.source == 'spot_search').count() or 0
    dynamic_statisitcs['critical_ports'] = query.where(FclFreightRateJobs.source == 'critical_ports').count() or 0
    dynamic_statisitcs['expiring_rates'] = query.where(FclFreightRateJobs.source == 'expiring_rates').count() or 0
    dynamic_statisitcs['cancelled_shipments'] = query.where(FclFreightRateJobs.source == 'cancelled_shipments').count() or 0
    query = query.where(FclFreightRateJobs.source == filters['source'])
    return dynamic_statisitcs, query
    
    
def get_data(query):
    return list(query.dicts())


def get_query(sort_by, sort_type, includes):
    if includes:
        fcl_all_fields = list(FclFreightRateJobs._meta.fields.keys())
        required_fcl_fields =  [a for a in includes.keys() if a in fcl_all_fields]
        fcl_fields = [getattr(FclFreightRateJobs, key) for key in required_fcl_fields]
    else:
        fcl_fields = [getattr(FclFreightRateJobs, key) for key in DEFAULT_REQUIRED_FIELDS]
    query = FclFreightRateJobs.select(*fcl_fields)
    if sort_by:
        query = query.order_by(
            eval("FclFreightRateJobs.{}.{}()".format(sort_by, sort_type))
        )

    return query


def apply_indirect_filters(query, filters):
    for key in filters:
        apply_filter_function = f"apply_{key}_filter"
        query = eval(f"{apply_filter_function}(query, filters)")
    return query


def apply_user_id_filter(query, filters):
    query = query.where(FclFreightRateJobs.assigned_to_id == filters["user_id"])


def apply_updated_at_filter(query, filters):
    query = query.where(FclFreightRateJobs.updated_at > filters["updated_at"])
    return query


def apply_date_range_filter(query, filters):
    if not filters["date_range"]["startDate"]:
        start_date = datetime.now() - timedelta(days=7)
    else:
        start_date = datetime.strptime(filters["date_range"]["startDate"],STRING_FORMAT) + timedelta(hours=5, minutes=30)
    if not filters["date_range"]["endDate"]:
        
        end_date = datetime.now() 
    else:
        end_date = datetime.strptime(filters["date_range"]["endDate"],STRING_FORMAT) + timedelta(hours=5, minutes=30)
    query = query.where(FclFreightRateJobs.created_at.cast("date") >= start_date.date(), FclFreightRateJobs.created_at.cast("date") <= end_date.date())
    return query
