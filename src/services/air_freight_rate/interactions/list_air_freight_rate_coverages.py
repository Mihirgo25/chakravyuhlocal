from services.air_freight_rate.models.air_freight_rate_jobs import AirFreightRateJobs
from services.envision.helpers.csv_link_generator import get_csv_url
import json
from libs.get_applicable_filters import get_applicable_filters
from libs.get_filters import get_filters
from libs.json_encoder import json_encoder

possible_direct_filters = [
    "origin_airport",
    "destination_airport_id",
    "airline_id",
    "commodity",
    "status",
]
possible_indirect_filters = ["updated_at", "user_id", "date_range"]

DYNAMIC_STATISTICS = {
    'monitoring_dashboard':0,
    'spot_search' : 0,
    'critical_ports' : 0,
    'expiring_rates' : 0,
    'cancelled_shipments' : 0
}

DEFAULT_REQUIRED_FIELDS = [
    'id',
    'assigned_to',
    'closed_by',
    'closing_remarks',
    'commodity',
    'created_at',
    'updated_at',
    'status',
    'airline',
    'service_provider',
    'origin_airport',
    'destination_airport',
    'shipment_type',
    'stacking_type'
]


def list_air_freight_rate_coverages(
    filters={},
    page_limit=10,
    page=1,
    sort_by="updated_at",
    sort_type="desc",
    generate_csv_url=False,
    includes = {}
):
    query = get_query(sort_by, sort_type, includes)
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)
        direct_filters, indirect_filters = get_applicable_filters(
            filters, possible_direct_filters, possible_indirect_filters
        )
        query = get_filters(direct_filters, query, AirFreightRateJobs)
        query = apply_indirect_filters(query, indirect_filters)
        dynamic_statisitcs, query = get_statisitcs(DYNAMIC_STATISTICS.copy(), query, filters)

    if page_limit and not generate_csv_url:
        query = query.paginate(page, page_limit)

    data = get_data(query)

    return {"list": data, "stats": dynamic_statisitcs}


def get_statisitcs(dynamic_statisitcs, query, filters):
    dynamic_statisitcs['monitoring_dashboard'] = query.where(AirFreightRateJobs.source == 'monitoring_dashboard').count()
    dynamic_statisitcs['spot_search'] = query.where(AirFreightRateJobs.source == 'spot_search').count()
    dynamic_statisitcs['critical_ports'] = query.where(AirFreightRateJobs.source == 'critical_ports').count()
    dynamic_statisitcs['expiring_rates'] = query.where(AirFreightRateJobs.source == 'expiring_rates').count()
    dynamic_statisitcs['cancelled_shipments'] = query.where(AirFreightRateJobs.source == 'cancelled_shipments').count()
    query = query.where(AirFreightRateJobs.source == filters['source'])
    return dynamic_statisitcs, query

def get_data(query):
    return list(query.dicts())


def get_query(sort_by, sort_type, includes):
    if includes:
        fcl_all_fields = list(AirFreightRateJobs._meta.fields.keys())
        required_fcl_fields =  [a for a in includes.keys() if a in fcl_all_fields]
        air_fields = [getattr(AirFreightRateJobs, key) for key in required_fcl_fields]
    else:
        air_fields = [getattr(AirFreightRateJobs, key) for key in DEFAULT_REQUIRED_FIELDS]
    query = AirFreightRateJobs.select(*air_fields)
    if sort_by:
        query = query.order_by(
            eval("AirFreightRateJobs.{}.{}()".format(sort_by, sort_type))
        )

    return query


def apply_indirect_filters(query, filters):
    for key in filters:
        apply_filter_function = f"apply_{key}_filter"
        query = eval(f"{apply_filter_function}(query, filters)")
    return query


def apply_user_id_filter(query, filters):
    query = query.where(AirFreightRateJobs.assigned_to_id == filters["user_id"])


def apply_updated_at_filter(query, filters):
    query = query.where(AirFreightRateJobs.updated_at > filters["updated_at"])
    return query


def apply_date_range_filter(query, filters):
    return query
