from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from database.db_session import db
from fastapi import FastAPI, Response, Query, Request, Depends
import json
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.interaction.create_fcl_freight_commodity_cluster import create_fcl_freight_commodity_cluster
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_local_agent import create_fcl_freight_rate_local_agent
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_not_available import create_fcl_freight_rate_not_available
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_task import create_fcl_freight_rate_task
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_request import create_fcl_freight_rate_request
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_local_request import create_fcl_freight_rate_local_request
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_feedback import create_fcl_freight_rate_feedback
from services.fcl_freight_rate.interaction.create_fcl_weight_slabs_configuration import create_fcl_weight_slabs_configuration
from services.fcl_freight_rate.interaction.get_fcl_freight_commodity_cluster import get_fcl_freight_commodity_cluster
from services.fcl_freight_rate.interaction.get_fcl_freight_rate import get_fcl_freight_rate
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_locals import list_fcl_freight_rate_locals
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_local_agents import list_fcl_freight_rate_local_agents
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_tasks import list_fcl_freight_rate_tasks
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_dislikes import list_fcl_freight_rate_dislikes
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_local import get_fcl_freight_rate_local
from services.fcl_freight_rate.interaction.get_fcl_freight_local_rate_cards import get_fcl_freight_local_rate_cards
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_cards import get_fcl_freight_rate_cards
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_addition_frequency import get_fcl_freight_rate_addition_frequency
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_suggestions import get_fcl_freight_rate_suggestions
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_visibility import get_fcl_freight_rate_visibility
# from database.create_tables import create_table
import time
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_bulk_operations import list_fcl_freight_rate_bulk_operations
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_requests import list_fcl_freight_rate_requests
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_feedbacks import list_fcl_freight_rate_feedbacks
from services.fcl_freight_rate.interaction.list_fcl_freight_commodity_clusters import list_fcl_freight_commodity_clusters
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_commodity_surcharges import list_fcl_freight_rate_commodity_surcharges
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_weight_limits import list_fcl_freight_rate_weight_limits
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_seasonal_surcharges import list_fcl_freight_rate_seasonal_surcharges
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_free_day_requests import list_fcl_freight_rate_free_day_requests
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_free_days import list_fcl_freight_rate_free_days
from services.fcl_freight_rate.interaction.list_fcl_weight_slabs_configuration import list_fcl_weight_slabs_configuration
from services.fcl_freight_rate.interaction.create_fcl_freight_rate import create_fcl_freight_rate_data
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate import delete_fcl_freight_rate
from services.fcl_freight_rate.interaction.extend_create_fcl_freight_rate import extend_create_fcl_freight_rate_data
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_extension_rule_set import update_fcl_freight_rate_extension_rule_set_data
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_extension_rule_sets import list_fcl_freight_rate_extension_rule_set_data
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_local_priority_scores import update_fcl_freight_rate_local_priority_scores_data
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_priority_scores import update_fcl_freight_rate_priority_scores_data
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_task import update_fcl_freight_rate_task_data
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_extension_rule_set import create_fcl_freight_rate_extension_rule_set_data
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_extension import get_fcl_freight_rate_extension_data
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_weight_limit import get_fcl_freight_rate_weight_limit
from services.fcl_freight_rate.interaction.update_fcl_freight_rate import update_fcl_freight_rate_data
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_local import create_fcl_freight_rate_local
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_local import update_fcl_freight_rate_local
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_weight_limit import create_fcl_freight_rate_weight_limit
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_free_day import create_fcl_freight_rate_free_day
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_weight_limit import update_fcl_freight_rate_weight_limit
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_free_day import get_fcl_freight_rate_free_day
from services.fcl_freight_rate.interaction.get_fcl_weight_slabs_configuration import get_fcl_weight_slabs_configuration
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_free_day import update_fcl_freight_rate_free_day
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_stats import get_fcl_freight_rate_stats
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_seasonal_surcharge import get_fcl_freight_rate_seasonal_surcharge
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_commodity_surcharge import get_fcl_freight_rate_commodity_surcharge
from services.fcl_freight_rate.interaction.get_fcl_freight_commodity_cluster import get_fcl_freight_commodity_cluster

# from services.fcl_freight_rate.interaction.create_fcl_freight_rate_task import create_fcl_freight_rate_task_data
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_request import delete_fcl_freight_rate_request
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_feedback import delete_fcl_freight_rate_feedback
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_local_request import delete_fcl_freight_rate_local_request
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_local import delete_fcl_freight_rate_local
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_free_day_request import delete_fcl_freight_rate_free_day_request
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_local_agent import update_fcl_freight_rate_local_agent
from services.fcl_freight_rate.interaction.update_fcl_weight_slabs_configuration import update_fcl_weight_slabs_configuration
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_platform_prices import update_fcl_freight_rate_platform_prices
from rails_client.client import initialize_client
from params import *
from database.create_tables import create_table
import time
from datetime import datetime
from services.fcl_freight_rate.interaction.list_fcl_freight_rates import list_fcl_freight_rates
# from services.fcl_freight_rate.interaction.get_fcl_freight_rate_local import get_fcl_freight_rate_local
from configs.defintions import yml_obj


app = FastAPI(debug=True)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_request_response_time(request: Request, call_next):
    from time import time
    start_time = time()
    response = await call_next(request)
    process_time = time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.on_event("startup")
def startup():
    if db.is_closed():
        db.connect()
    # create_table()
    initialize_client()
    
@app.on_event("shutdown")
def shutdown():
    if not db.is_closed():
        db.close()

@app.get("/")
def read_root():
    return "WELCOME TO OCEAN RMS"

@app.post("/create_fcl_freight_commodity_cluster")
def create_fcl_freight_commodity_cluster_data(request: CreateFclFreightCommodityCluster):
    data = create_fcl_freight_commodity_cluster(request)
    return data

@app.post("/create_fcl_freight_rate_local_agent")
def create_fcl_freight_rate_local_agent_data(request: CreateFclFreightRateLocalAgent):
    data = create_fcl_freight_rate_local_agent(request.__dict__)
    return data

@app.post("/create_fcl_freight_rate")
def create_fcl_freight_rate_test(request: PostFclFreightRate):
    # try:
        rate = create_fcl_freight_rate_data(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(rate))
    # except Exception as e:
        # logger.error(e,exc_info=True)
    #     return JSONResponse(status_code=500, content={"success": False})

@app.post("/create_fcl_freight_rate_feedback")
def create_fcl_freight_rate_feedback_data(request: CreateFclFreightRateFeedback):
    rate_id = create_fcl_freight_rate_feedback(request)
    return rate_id

@app.post("/create_fcl_freight_rate_not_available")
def create_fcl_freight_rate_not_available_data(request: CreateFclFreightRateNotAvailable):
    data = create_fcl_freight_rate_not_available(request)
    if data == True:
        return JSONResponse(status_code = 200, content = {'success': True})
    else:
        return JSONResponse(status_code = 500, content = {'success' :  False})


@app.post("/create_fcl_freight_rate_local")
def create_fcl_freight_rate_local_data(request: PostFclFreightRateLocal, response: Response):
    data = create_fcl_freight_rate_local(request.dict(exclude_none=False))
    return data

@app.post("/create_fcl_freight_rate_task")
def create_fcl_freight_rate_task_data(request: CreateFclFreightRateTask):
    data = create_fcl_freight_rate_task(request)
    return data

@app.post("/create_fcl_freight_rate_request")
def create_fcl_freight_rate_request_data(request: CreateFclFreightRateRequest):
    data = create_fcl_freight_rate_request(request)
    return data

@app.post("/create_fcl_freight_rate_local_request")
def create_fcl_freight_rate_local_request_data(request: CreateFclFreightRateLocalRequest):
    data = create_fcl_freight_rate_local_request(request)
    return data

@app.post("/create_fcl_weight_slabs_configuration")
def create_fcl_weight_slabs_configuration_data(request: CreateFclWeightSlabsConfiguration):
    data = create_fcl_weight_slabs_configuration(request.dict(exclude_none = False))
    return data

@app.get("/get_fcl_freight_commodity_cluser")
def get_fcl_freight_commodity_cluster_data(id: str):
    try:
        data = get_fcl_freight_commodity_cluster(id)
        data = jsonable_encoder(data)
        return JSONResponse(status_code = 200, content = data)
    except:
        return JSONResponse(status_code = 500, content = {'success' : False})

@app.get("/get_fcl_freight_rate_data")
def get_fcl_freight_rate_data(origin_port_id: str = None, origin_main_port_id: str = None, destination_port_id: str = None, destination_main_port_id: str = None, container_size: str = None, container_type: str = None, commodity: str = None, shipping_line_id: str = None, service_provider_id: str = None, importer_exporter_id: str = None):
    request = {
        'origin_port_id':origin_port_id,
        'origin_main_port_id':origin_main_port_id,
        'destination_port_id':destination_port_id,
        'destination_main_port_id' : destination_main_port_id,
        'container_size' : container_size, 
        'container_type' : container_type, 
        'commodity' : commodity,
        'shipping_line_id' : shipping_line_id,
        'service_provider_id': service_provider_id, 
        'importer_exporter_id': importer_exporter_id
    }
    data = get_fcl_freight_rate(request)
    data = jsonable_encoder(data)
    return JSONResponse(status_code=200, content=data)

@app.get("/get_fcl_freight_rate_local")
def get_fcl_freight_local_data(port_id: str = None, main_port_id: str = None, trade_type: str = None, container_size: str = None, container_type: str = None, commodity: str = None, shipping_line_id: str = None, service_provider_id: str = None):
    request = {
        'port_id':port_id,
        'main_port_id':main_port_id,
        'trade_type':trade_type,
        'container_size' : container_size, 
        'container_type' : container_type, 
        'commodity' : commodity,
        'shipping_line_id' : shipping_line_id,
        'service_provider_id': service_provider_id
    }
    try:
        data = get_fcl_freight_rate_local(request)
        data = jsonable_encoder(data)
        return JSONResponse(status_code=200, content = data)
    except:
        return JSONResponse(status_code=500, content = {'success':False})

@app.post("/get_fcl_freight_local_rate_cards")
def get_fcl_freight_local_rate_cards_data(trade_type: str, port_id: str, country_id: str, container_size: str, container_type: str, containers_count: int,  bls_count: int, commodity: str = None, shipping_line_id: str = None, service_provider_id: str = None, rates: list[str] = [], include_confirmed_inventory_rates: bool =False, additional_services: list[str] = [], include_destination_dpd: bool = False, cargo_weight_per_container: int = None):
    request = {
        'trade_type':trade_type,
        'port_id':port_id,
        'country_id':country_id,
        'container_size' : container_size, 
        'container_type' : container_type, 
        'containers_count' : containers_count,
        'bls_count' : bls_count,
        'commodity' : commodity,
        'shipping_line_id' : shipping_line_id,
        'service_provider_id': service_provider_id, 
        'rates':rates,
        'cargo_weight_per_container': cargo_weight_per_container,
        'include_destination_dpd' : include_destination_dpd,
        'additional_services':additional_services,
        'include_confirmed_inventory_rates':include_confirmed_inventory_rates,
    }
    data = get_fcl_freight_local_rate_cards(request)

    return data

@app.post("/get_fcl_freight_rate_cards")
def get_fcl_freight_rate_cards_data(origin_port_id: str, origin_country_id: str, destination_port_id: str, destination_country_id: str,  trade_type: str, importer_exporter_id: str, include_origin_local: bool, include_destination_local: bool, container_size: str, container_type: str, containers_count: int,  bls_count: int, validity_start: str, validity_end: str, commodity: str = None, shipping_line_id: str = None, service_provider_id: str = None, include_confirmed_inventory_rates: bool =False, additional_services: str = None, ignore_omp_dmp_sl_sps: str = None, include_destination_dpd: bool = False, cargo_weight_per_container: int = None, cogo_entity_id: str = None):
    if additional_services:
        additional_services = json.loads(additional_services)
    else:
        additional_services = []
    if ignore_omp_dmp_sl_sps:
        ignore_omp_dmp_sl_sps = json.loads(ignore_omp_dmp_sl_sps)
    else:
        ignore_omp_dmp_sl_sps = []
    validity_start = datetime.strptime(validity_start,'%Y-%m-%d')
    validity_end = datetime.strptime(validity_end,'%Y-%m-%d')
    request = {
        'origin_port_id' : origin_port_id,
        'origin_country_id' : origin_country_id,
        'destination_port_id': destination_port_id,
        'destination_country_id': destination_country_id,
        'container_size' : container_size, 
        'container_type' : container_type, 
        'containers_count' : containers_count,
        'bls_count' : bls_count,
        'commodity' : commodity,
        'importer_exporter_id' : importer_exporter_id,
        'trade_type' : trade_type,
        'shipping_line_id' : shipping_line_id,
        'service_provider_id': service_provider_id, 
        'validity_start' : validity_start,
        'validity_end' : validity_end,
        'include_origin_local' : include_origin_local,
        'include_destination_local': include_destination_local,
        'cargo_weight_per_container': cargo_weight_per_container,
        'include_destination_dpd' : include_destination_dpd,
        'additional_services':additional_services,
        'include_confirmed_inventory_rates':include_confirmed_inventory_rates,
        'ignore_omp_dmp_sl_sps' : ignore_omp_dmp_sl_sps,
        'cogo_entity_id' : cogo_entity_id
    }
    data = get_fcl_freight_rate_cards(request)
    return data

@app.get("/get_fcl_freight_rate_addition_frequency")
def get_fcl_freight_rate_addition_frequency_data(
    group_by: str,
    filters: str = None,
    sort_type: str = 'desc'
):
    data = get_fcl_freight_rate_addition_frequency(filters, sort_type, group_by)
    return data

@app.get("/get_fcl_freight_rate_suggestions")
def get_fcl_freight_rate_suggestions_data(
    validity_start: str,
    validity_end: str,
    searched_origin_port_id: str = None,
    searched_destination_port_id: str = None,
    filters: str = None
):
    data = get_fcl_freight_rate_suggestions(validity_start, validity_end, searched_origin_port_id, searched_destination_port_id, filters)
    return data

@app.get("/get_fcl_freight_rate_visibility")
def get_fcl_freight_rate_visibility_data(
    service_provider_id: str,
    origin_port_id: str = None,
    destination_port_id: str = None,
    from_date: str = None,
    to_date: str = None,
    rate_id: str = None,
    shipping_line_id: str = None,
    container_size: str = None,
    container_type: str = None,
    commodity: str = None
):
    data = get_fcl_freight_rate_visibility(service_provider_id, origin_port_id, destination_port_id, from_date, to_date, rate_id, shipping_line_id, container_size, container_type, commodity)
    return data

@app.get("/get_fcl_weight_slabs_configuration")
def get_fcl_weight_slabs_configuration_data(filters: str = None):
    # try:
    data = get_fcl_weight_slabs_configuration(filters)
    data = jsonable_encoder(data)
    return JSONResponse(status_code = 200, content = data)
    # except:
    #     return JSONResponse(status_code = 500, content = {'success' : False})

@app.get("/list_fcl_freight_rate_bulk_operations")
def list_fcl_freight_rate_bulk_operations_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1
    ):
    data = list_fcl_freight_rate_bulk_operations(filters, page_limit, page)
    return data 

@app.get("/list_fcl_freight_rate_free_day_requests")
def list_fcl_freight_rate_free_day_requests_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    is_stats_required: bool = True,
    performed_by_id: str = None,
    spot_search_details_required: bool = False
    ):
    data = list_fcl_freight_rate_free_day_requests(filters, page_limit, page, is_stats_required, performed_by_id, spot_search_details_required)
    return data

@app.get("/list_fcl_freight_rates")
def list_fcl_freight_rates_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = 'priority_score',
    sort_type: str = 'desc',
    pagination_data_required: bool = True,
    return_query: bool = False,
    expired_rates_required: bool = False,
    all_rates_for_cogo_assured: bool = False
):
    data = list_fcl_freight_rates(filters, page_limit, page, sort_by, sort_type, pagination_data_required, return_query, expired_rates_required, all_rates_for_cogo_assured)
    return data

@app.get("/list_fcl_freight_rate_locals")
def list_fcl_freight_rate_locals_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = 'priority_score',
    sort_type: str = 'desc',
    return_query: bool = False
):
    a = time.time()
    data = list_fcl_freight_rate_locals(filters, page_limit, page, sort_by, sort_type, return_query)
    print(time.time() - a)
    return data

@app.get("/list_fcl_freight_rate_local_agent")
def list_fcl_freight_rate_local_agent_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = 'updated_at',
    sort_type: str = 'desc',
    pagination_data_required: bool = True,
    add_service_objects_required: bool = True):
    try:
        data = list_fcl_freight_rate_local_agents(filters, page_limit, page, sort_by, sort_type, pagination_data_required, add_service_objects_required)
        data = jsonable_encoder(data)
        return JSONResponse(status_code = 200, content = data)
    except:
        return JSONResponse(status_code = 500, content = {'success':False})

@app.get("/list_fcl_freight_rate_tasks")
def list_fcl_freight_rate_tasks_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = 'created_at',
    sort_type: str = 'desc',
    stats_required: bool = True,
    pagination_data_required: bool = True
):
    data = list_fcl_freight_rate_tasks(filters, page_limit, page, sort_by, sort_type, stats_required, pagination_data_required)
    return data

@app.get("/list_fcl_freight_rate_requests")
def list_fcl_freight_rate_requests_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    performed_by_id: str = None,
    is_stats_required: bool = True,
    spot_search_details_required: bool = False
    ):
    data = list_fcl_freight_rate_requests(filters, page_limit, page, performed_by_id, is_stats_required, spot_search_details_required)
    return data

@app.get("/list_fcl_freight_rate_seasonal_surcharges")
def list_fcl_freight_rate_seasonal_surcharges_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    pagination_data_required: bool = True
    ):
    data = list_fcl_freight_rate_seasonal_surcharges(filters, page_limit, page, pagination_data_required)
    return data


@app.get("/list_fcl_freight_rate_feedbacks")
def list_fcl_freight_rate_feedbacks_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    performed_by_id: str = None,
    is_stats_required: bool = True,
    spot_search_details_required: bool = False
    ):
    data = list_fcl_freight_rate_feedbacks(filters, page_limit, page, performed_by_id, is_stats_required, spot_search_details_required)
    return data


@app.get("/list_fcl_freight_rate_commodity_clusters")
def list_fcl_freight_rate_commodity_clusters_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    pagination_data_required: bool = True,
    sort_by: str = 'updated_at',
    sort_type: str = 'desc'
    ):
    data = list_fcl_freight_commodity_clusters(filters, page_limit, page, pagination_data_required, sort_by, sort_type)
    return data

@app.get("/list_fcl_freight_rate_commodity_surcharges")
def list_fcl_freight_rate_commodity_surcharges_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    pagination_data_required: bool = True
    ):
    data = list_fcl_freight_rate_commodity_surcharges(filters, page_limit, page, pagination_data_required)
    return data

@app.get("/list_fcl_freight_rate_dislikes")
def list_fcl_freight_rate_dislikes_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1
    ):
    data = list_fcl_freight_rate_dislikes(filters, page_limit, page)
    return data

@app.get("/list_fcl_freight_rate_free_days")
def list_fcl_freight_rate_free_days_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    pagination_data_required: bool = True,
    return_query: bool = False
    ):
    data = list_fcl_freight_rate_free_days(filters, page_limit, page, pagination_data_required, return_query)
    return data

@app.get("/list_fcl_freight_rate_weight_limits")
def list_fcl_freight_rate_weight_limits_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    pagination_data_required: bool = True
    ):
    data = list_fcl_freight_rate_weight_limits(filters, page_limit, page, pagination_data_required)
    return data

@app.get("/list_fcl_weight_slabs_configuration")
def list_fcl_weight_slabs_configuration_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    pagination_data_required: bool = True
    ):
    data = list_fcl_weight_slabs_configuration(filters, page_limit, page, pagination_data_required)
    return data

@app.post("/update_fcl_freight_rate")
def update_fcl_freight_rate(request: UpdateFclFreightRate, response: Response):
    rate = update_fcl_freight_rate_data(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content={"success": True})

@app.put("/update_fcl_freight_rate_local")
def update_fcl_freight_rate_local_data(request: UpdateFclFreightRateLocal, response: Response):
    data = update_fcl_freight_rate_local(request.dict(exclude_none=True))
    return data

@app.put("/update_fcl_freight_rate_local_agent")
def update_fcl_freight_rate_local_agent_data(request: UpdateFclFreightRateLocalAgent):
    data = update_fcl_freight_rate_local_agent(request.__dict__)
    data = jsonable_encoder(data)
    return data

@app.put("/update_fcl_freight_slabs_configuration")
def update_fcl_freight_slabs_configuration_data(request: UpdateFclWeightSlabsConfiguration):
    data = update_fcl_weight_slabs_configuration(request.dict(exclude_none=True))
    data = jsonable_encoder(data)
    return data

@app.put("/update_fcl_freight_rate_platform_prices")
def update_fcl_freight_rate_platform_prices_data(request: UpdateFclFreightRatePlatformPrices):
    data = update_fcl_freight_rate_platform_prices(request.dict(exclude_none=False))
    data = jsonable_encoder(data)
    return data

@app.delete("/delete_fcl_freight_rate")
def delete_fcl_freight_rates(request: DeleteFclFreightRate, response: Response):
    delete_rate = delete_fcl_freight_rate(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content={"success": True})

@app.post("/create_fcl_freight_rate_extension_rule_set")
def create_fcl_freight_rate_extension_rule_set(request: PostFclFreightRateExtensionRuleSet):
    return create_fcl_freight_rate_extension_rule_set_data(request)

@app.post("/extend_create_fcl_freight_rate")
def extend_create_fcl_freight_rate(request: ExtendCreateFclFreightRate):
    return extend_create_fcl_freight_rate_data(request)

@app.post("/update_fcl_freight_rate_extension_rule_set")
def update_fcl_freight_rate_extension_rule_set(request: UpdateFclFreightRateExtensionRuleSet):
    return update_fcl_freight_rate_extension_rule_set_data(request)

@app.get("/list_fcl_freight_rate_extension_rule_set")
def list_fcl_freight_rate_extension_rule_set(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = 'updated_at',
    sort_type: str = 'desc'
):
    try:
        data =  list_fcl_freight_rate_extension_rule_set_data(filters, page_limit, page, sort_by, sort_type)
        data = jsonable_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except:
        return JSONResponse(status_code=500, content={'success':False})


@app.get("/get_fcl_freight_rate_extension")
def get_fcl_freight_rate_extension(
    service_provider_id: str,
    shipping_line_id: str,
    origin_port_id: str,
    destination_port_id: str,
    commodity: str,
    container_size: str,
    container_type:str = None
  ):
    try:
        data = get_fcl_freight_rate_extension_data(service_provider_id, shipping_line_id, origin_port_id, destination_port_id, commodity, container_size, container_type)
        data = jsonable_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except:
        return JSONResponse(status_code=500, content={'success':False})


# @app.post("/update_fcl_freight_rate_task")
# def update_fcl_freight_rate_task(request: UpdateFclFreightRateTask):
#     return update_fcl_freight_rate_task_data(request)

# @app.post("/create_fcl_freight_rate_task")
# def create_fcl_freight_rate_task(request: CreateFclFreightRateTask):
#     return create_fcl_freight_rate_task_data(request)

@app.delete("/delete_fcl_freight_rate_request")
def delete_fcl_freight_rates_request(request: DeleteFclFreightRateRequest, response: Response):
    delete_rate = delete_fcl_freight_rate_request(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content={"success": True})

@app.delete("/delete_fcl_freight_rate_feedback")
def delete_fcl_freight_rates_feedback(request: DeleteFclFreightRateFeedback, response: Response):
    delete_rate = delete_fcl_freight_rate_feedback(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content={"success": True})

@app.delete("/delete_fcl_freight_rate_local_request")
def delete_fcl_freight_rates_local_request(request: DeleteFclFreightRateLocalRequest, response: Response):
    delete_rate = delete_fcl_freight_rate_local_request(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content={"success": True})

@app.delete("/delete_fcl_freight_rate_local")
def delete_fcl_freight_rates_local(request: DeleteFclFreightRateLocal, response: Response):
    delete_rate = delete_fcl_freight_rate_local(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content={"success": True})

@app.delete("/delete_fcl_freight_rate_free_day_request")
def delete_fcl_freight_rates_free_day_request(request: DeleteFclFreightRateFreeDayRequest, response: Response):
    delete_rate = delete_fcl_freight_rate_free_day_request(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content={"success": True})


@app.post("/create_fcl_freight_rate_weight_limit")
def create_fcl_freight_rate_weight_limit_data(request: CreateFclFreightRateWeightLimit):
    return create_fcl_freight_rate_weight_limit(request.dict(exclude_none=False))

@app.get("/get_fcl_freight_rate_weight_limit")
def get_fcl_freight_rate_weight_limit_data(
    origin_location_id: str = None,
    destination_location_id: str = None,
    container_size: str = None,
    container_type: str = None,
    shipping_line_id: str = None,
    service_provider_id: str = None
): 
    request = {
        'origin_location_id':origin_location_id,
        'destination_location_id':destination_location_id,
        'container_size':container_size,
        'container_type':container_type,
        'shipping_line_id': shipping_line_id,
        'service_provider_id':service_provider_id
    }
    data = get_fcl_freight_rate_weight_limit(request)
    return data

@app.put("/update_fcl_freight_rate_weight_limit")
def update_fcl_freight_rate_weight_limit_data(request: UpdateFclFreightRateWeightLimit):
    data = update_fcl_freight_rate_weight_limit(request.dict(exclude_none=False))
    return data

@app.post("/create_fcl_freight_rate_free_day")
def create_fcl_freight_rate_free_day_data(request: CreateFclFreightRateFreeDay):
    data = create_fcl_freight_rate_free_day(request.dict(exclude_none=False))
    return data

@app.get("/get_fcl_freight_rate_free_day")
def get_fcl_freight_rate_free_day_data(
    location_id: str = None,
    trade_type: str = None,
    free_days_type: str = None,
    container_size: str = None,
    container_type: str = None,
    shipping_line_id: str = None,
    service_provider_id: str = None,
    importer_exporter_id: str = None
):
    request = {
        'location_id':location_id,
        'trade_type':trade_type,
        'free_days_type':free_days_type,
        'container_size':container_size,
        'container_type':container_type,
        'shipping_line_id': shipping_line_id,
        'service_provider_id':service_provider_id,
        'importer_exporter_id':importer_exporter_id
    }
    data = get_fcl_freight_rate_free_day(request)
    return data

@app.put("/update_fcl_freight_rate_free_day")
def update_fcl_freight_rate_free_day_data(request: UpdateFclFreightRateFreeDay):
    data = update_fcl_freight_rate_free_day(request.dict(exclude_none=False))
    return data

@app.get("/get_fcl_freight_rate_stats")
def get_fcl_freight_rate_stats_data(
    validity_start: datetime,
    validity_end: datetime,
    stats_types: str
):
    request = {
        'validity_start':validity_start,
        'validity_end':validity_end,
        'stats_types':stats_types
    }
    data = get_fcl_freight_rate_stats(request)
    return data

@app.get("/get_fcl_freight_rate_seasonal_surcharge")
def get_fcl_freight_rate_seasonal_surcharge_data(
    origin_location_id: str = None,
    destination_location_id: str = None,
    container_size: str = None,
    container_type: str = None,
    code: str = None,
    shipping_line_id: str = None,
    service_provider_id: str = None
):
    request = {
        'origin_location_id':origin_location_id,
        'destination_location_id':destination_location_id,
        'container_size':container_size,
        'container_type':container_type,
        'code':code,
        'shipping_line_id':shipping_line_id,
        'service_provider_id':service_provider_id
    }
    data = get_fcl_freight_rate_seasonal_surcharge(request)
    return data

@app.get("/get_fcl_freight_rate_commodity_surcharge")
def get_fcl_freight_rate_commodity_surcharge_data(
    origin_location_id: str = None,
    destination_location_id: str = None,
    container_size: str = None,
    container_type: str = None,
    commodity: str = None,
    shipping_line_id: str = None,
    service_provider_id: str = None
):
    request = {
        'origin_location_id':origin_location_id,
        'destination_location_id':destination_location_id,
        'container_size':container_size,
        'container_type':container_type,
        'commodity':commodity,
        'shipping_line_id':shipping_line_id,
        'service_provider_id':service_provider_id
    }
    data = get_fcl_freight_rate_commodity_surcharge(request)
    return data

@app.get("/get_fcl_freight_commodity_cluster")
def get_fcl_freight_commodity_cluster_data(
    id: str = None
):
    request = {
        'id':id
    }
    data = get_fcl_freight_commodity_cluster(request)
    return data