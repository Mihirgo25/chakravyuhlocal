from fastapi import APIRouter, Query, Depends
from fastapi.responses import JSONResponse
from typing import Union, List
import json
from fastapi.encoders import jsonable_encoder
from params import *
from datetime import datetime
from rms_utils.auth import authorize_token

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
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_audits import list_fcl_freight_rate_audits
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_bulk_operations import list_fcl_freight_rate_bulk_operations
from services.fcl_freight_rate.interaction.list_dashboard_fcl_freight_rates import list_dashboard_fcl_freight_rates
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_requests import list_fcl_freight_rate_requests
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_local_requests import list_fcl_freight_rate_local_requests
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_feedbacks import list_fcl_freight_rate_feedbacks
from services.fcl_freight_rate.interaction.list_fcl_freight_commodity_clusters import list_fcl_freight_commodity_clusters
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_commodity_surcharges import list_fcl_freight_rate_commodity_surcharges
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_weight_limits import list_fcl_freight_rate_weight_limits
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_seasonal_surcharges import list_fcl_freight_rate_seasonal_surcharges
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_free_day_requests import list_fcl_freight_rate_free_day_requests
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_free_days import list_fcl_freight_rate_free_days
from services.fcl_freight_rate.interaction.list_fcl_weight_slabs_configuration import list_fcl_weight_slabs_configuration
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_local_suggestions import list_fcl_freight_rate_local_suggestions
from services.fcl_freight_rate.interaction.create_fcl_freight_rate import create_fcl_freight_rate_data
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate import delete_fcl_freight_rate
from services.fcl_freight_rate.interaction.extend_create_fcl_freight_rate import extend_create_fcl_freight_rate_data
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_extension_rule_set import update_fcl_freight_rate_extension_rule_set_data
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_extension_rule_sets import list_fcl_freight_rate_extension_rule_set_data
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
from services.fcl_freight_rate.interaction.get_eligible_fcl_freight_rate_free_day import get_eligible_fcl_freight_rate_free_day
from services.fcl_freight_rate.interaction.get_fcl_weight_slabs_configuration import get_fcl_weight_slabs_configuration
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_free_day import update_fcl_freight_rate_free_day
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_stats import get_fcl_freight_rate_stats
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_seasonal_surcharge import get_fcl_freight_rate_seasonal_surcharge
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_commodity_surcharge import get_fcl_freight_rate_commodity_surcharge
from services.fcl_freight_rate.interaction.get_fcl_freight_commodity_cluster import get_fcl_freight_commodity_cluster
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_bulk_operation import create_fcl_freight_rate_bulk_operation
# from services.fcl_freight_rate.interaction.create_fcl_freight_rate_task import create_fcl_freight_rate_task_data
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_request import delete_fcl_freight_rate_request
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_feedback import delete_fcl_freight_rate_feedback
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_local_request import delete_fcl_freight_rate_local_request
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_local import delete_fcl_freight_rate_local
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_free_day_request import delete_fcl_freight_rate_free_day_request
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_local_agent import update_fcl_freight_rate_local_agent
from services.fcl_freight_rate.interaction.update_fcl_weight_slabs_configuration import update_fcl_weight_slabs_configuration
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_platform_prices import update_fcl_freight_rate_platform_prices
from services.fcl_freight_rate.interaction.update_fcl_freight_commodity_cluster import update_fcl_freight_commodity_cluster
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_commodity_surcharge import update_fcl_freight_rate_commodity_surcharge
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_free_day_request import create_fcl_freight_rate_free_day_request
from services.fcl_freight_rate.interaction.list_fcl_freight_rates import list_fcl_freight_rates
from configs.definitions import yml_obj
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_commodity_surcharge import create_fcl_freight_rate_commodity_surcharge
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_seasonal_surcharge import create_fcl_freight_rate_seasonal_surcharge
from configs.env import APP_ENV

from services.rate_sheet.interactions.create_rate_sheet import create_rate_sheet
from services.rate_sheet.interactions.update_rate_sheet import update_rate_sheet
from services.rate_sheet.interactions.list_rate_sheets import list_rate_sheets

fcl_freight_router = APIRouter()

@fcl_freight_router.post("/create_fcl_freight_commodity_cluster")
def create_fcl_freight_commodity_cluster_data(request: CreateFclFreightCommodityCluster, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    data = create_fcl_freight_commodity_cluster(request.dict(exclude_none=False))
    # try:
    data = create_fcl_freight_commodity_cluster(request.dict(exclude_none=False))
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except Exception as e:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.post("/create_fcl_freight_rate_commodity_surcharge")
def create_fcl_freight_rate_commodity_surcharge_data(request: CreateFclFreightRateCommoditySurcharge, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    rate = create_fcl_freight_rate_commodity_surcharge(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content=jsonable_encoder(rate))
    # except Exception as e:
    #     return JSONResponse(status_code=500, content={"success": False})


@fcl_freight_router.post("/create_fcl_freight_rate_local_agent")
def create_fcl_freight_rate_local_agent_data(request: CreateFclFreightRateLocalAgent, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    data = create_fcl_freight_rate_local_agent(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.post("/create_fcl_freight_rate")
def create_fcl_freight_rate_func(request: PostFclFreightRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = create_fcl_freight_rate_data(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(rate))
    except Exception as e:
        raise e

@fcl_freight_router.post("/create_fcl_freight_rate_feedback")
def create_fcl_freight_rate_feedback_data(request: CreateFclFreightRateFeedback, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    rate_id = create_fcl_freight_rate_feedback(request)
    return JSONResponse(status_code=200, content=jsonable_encoder(rate_id))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.post("/create_fcl_freight_rate_not_available")
def create_fcl_freight_rate_not_available_data(request: CreateFclFreightRateNotAvailable, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    data = create_fcl_freight_rate_not_available(request)
    if data == True:
        return JSONResponse(status_code = 200, content = {'success': True})
    else:
        return JSONResponse(status_code = 500, content = {'success' :  False})


@fcl_freight_router.post("/create_fcl_freight_rate_local")
def create_fcl_freight_rate_local_data(request: PostFclFreightRateLocal, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    data = create_fcl_freight_rate_local(request.dict(exclude_none=False))
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.post("/create_fcl_freight_rate_task")
def create_fcl_freight_rate_task_data(request: CreateFclFreightRateTask, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    data = create_fcl_freight_rate_task(request)
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.post("/create_fcl_freight_rate_request")
def create_fcl_freight_rate_request_data(request: CreateFclFreightRateRequest, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    data = create_fcl_freight_rate_request(request)
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.post("/create_fcl_freight_rate_local_request")
def create_fcl_freight_rate_local_request_data(request: CreateFclFreightRateLocalRequest, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    data = create_fcl_freight_rate_local_request(request)
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.post("/create_fcl_weight_slabs_configuration")
def create_fcl_weight_slabs_configuration_data(request: CreateFclWeightSlabsConfiguration, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    data = create_fcl_weight_slabs_configuration(request.dict(exclude_none = False))
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.get("/get_fcl_freight_rate")
def get_fcl_freight_rate_data(
    origin_port_id: str = None,
    origin_main_port_id: str = None,
    destination_port_id: str = None,
    destination_main_port_id: str = None,
    container_size: str = None,
    container_type: str = None,
    commodity: str = None,
    shipping_line_id: str = None,
    service_provider_id: str = None,
    importer_exporter_id: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
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

    # try:
    data = get_fcl_freight_rate(request)
    data = jsonable_encoder(data)
    return JSONResponse(status_code=200, content=data)
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.get("/get_fcl_freight_rate_local")
def get_fcl_freight_local_data(
    port_id: str = None,
    main_port_id: str = None,
    trade_type: str = None,
    container_size: str = None,
    container_type: str = None,
    commodity: str = None,
    shipping_line_id: str = None,
    service_provider_id: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
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

    # try:
    data = get_fcl_freight_rate_local(request)
    data = jsonable_encoder(data)
    return JSONResponse(status_code=200, content = data)
    # except:
    #     return JSONResponse(status_code=500, content = {'success':False})

@fcl_freight_router.get("/get_fcl_freight_local_rate_cards")
def get_fcl_freight_local_rate_cards_data(
    trade_type: str,
    port_id: str,
    country_id: str,
    container_size: str,
    container_type: str,
    containers_count: int,
    bls_count: int,
    commodity: str = None,
    shipping_line_id: str = None,
    service_provider_id: str = None,
    rates: List[str] | None= Query(None),
    include_confirmed_inventory_rates: bool =False,
    additional_services: List[str] | None= Query(None),
    include_destination_dpd: bool = False,
    cargo_weight_per_container: int = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    if additional_services and len(additional_services) == 1 and not additional_services[0]:
        additional_services = []
    if rates and len(rates) == 1 and not rates[0]:
        rates = []

    request = {
        'trade_type':trade_type,
        'port_id':port_id,
        'country_id':country_id,
        'container_size' : container_size,
        'container_type' : container_type,
        'containers_count' : containers_count,
        'bls_count' : bls_count,
        'commodity' : commodity,
        'shipping_line_id' : shipping_line_id or None,
        'service_provider_id': service_provider_id or None,
        'rates':rates or [],
        'cargo_weight_per_container': cargo_weight_per_container,
        'include_destination_dpd' : include_destination_dpd,
        'additional_services': additional_services or [],
        'include_confirmed_inventory_rates':include_confirmed_inventory_rates,
    }

    try:
        data = get_fcl_freight_local_rate_cards(request)
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except Exception as e:
        raise e

@fcl_freight_router.get("/get_fcl_freight_rate_cards")
def get_fcl_freight_rate_cards_data(
    origin_port_id: str,
    origin_country_id: str,
    destination_port_id: str,
    destination_country_id: str,
    container_size: str,
    container_type: str,
    containers_count: int,
    validity_start: str,
    validity_end: str,
    trade_type: str = None,
    include_destination_local: bool = True,
    include_origin_local: bool = True,
    cogo_entity_id: str = None,
    importer_exporter_id: str = None,
    bls_count: int = 1,
    commodity: str = None,
    shipping_line_id: str = None,
    service_provider_id: str = None,
    include_confirmed_inventory_rates: bool =False,
    additional_services: str = None,
    ignore_omp_dmp_sl_sps: str = None,
    include_destination_dpd: bool = False,
    cargo_weight_per_container: int = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

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

    # try:
    data = get_fcl_freight_rate_cards(request)
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.get("/get_fcl_freight_rate_addition_frequency")
def get_fcl_freight_rate_addition_frequency_data(
    group_by: str,
    filters: str = None,
    sort_type: str = 'desc',
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    # try:
    data = get_fcl_freight_rate_addition_frequency( group_by, filters, sort_type)
    data = jsonable_encoder(data)
    return JSONResponse(status_code=200, content=data)
    # except:
    #     return JSONResponse(status_code=500, content={'success':False})

@fcl_freight_router.get("/get_fcl_freight_rate_suggestions")
def get_fcl_freight_rate_suggestions_data(
    validity_start: str,
    validity_end: str,
    searched_origin_port_id: str = None,
    searched_destination_port_id: str = None,
    filters: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    # try:
    data = get_fcl_freight_rate_suggestions(validity_start, validity_end, searched_origin_port_id, searched_destination_port_id, filters)
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.get("/get_fcl_freight_rate_visibility")
def get_fcl_freight_rate_visibility_data(
    service_provider_id: str,
    origin_port_id: str = None,
    destination_port_id: str = None,
    from_date: datetime = None,
    to_date: datetime = None,
    rate_id: str = None,
    shipping_line_id: str = None,
    container_size: str = None,
    container_type: str = None,
    commodity: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        'service_provider_id' : service_provider_id,
        'origin_port_id': origin_port_id,
        'destination_port_id': destination_port_id,
        'from_date': from_date,
        'to_date': to_date,
        'rate_id': rate_id,
        'shipping_line_id': shipping_line_id,
        'container_size': container_size,
        'container_type': container_type,
        'commodity': commodity
    }
    # try:
    data = get_fcl_freight_rate_visibility(request)
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.get("/get_fcl_weight_slabs_configuration")
def get_fcl_weight_slabs_configuration_data(filters: str = None, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    # try:
    data = get_fcl_weight_slabs_configuration(filters)
    data = jsonable_encoder(data)
    return JSONResponse(status_code = 200, content = data)
    # except:
    #     return JSONResponse(status_code = 500, content = {'success' : False})

@fcl_freight_router.get("/list_dashboard_fcl_freight_rates")
def list_dashboard_fcl_freight_rates_data(resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    # try:
    data = list_dashboard_fcl_freight_rates()
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.get("/list_fcl_freight_rate_audits")
def list_fcl_freight_audits_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = 'created_at',
    sort_type: str = 'asc',
    pagination_data_required: bool = False,
    user_data_required: bool = False,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    # try:
    data = list_fcl_freight_rate_audits(filters, page_limit, page, sort_by, sort_type, pagination_data_required, user_data_required)
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.get("/list_fcl_freight_rate_bulk_operations")
def list_fcl_freight_rate_bulk_operations_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    resp: dict = Depends(authorize_token)
    ):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    # try:
    data = list_fcl_freight_rate_bulk_operations(filters, page_limit, page)
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.get("/list_fcl_freight_rate_free_day_requests")
def list_fcl_freight_rate_free_day_requests_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    is_stats_required: bool = True,
    performed_by_id: str = None,
    resp: dict = Depends(authorize_token)
    ):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    # try:
    data = list_fcl_freight_rate_free_day_requests(filters, page_limit, page, is_stats_required, performed_by_id)
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.get("/list_fcl_freight_rates")
def list_fcl_freight_rates_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = 'updated_at',
    sort_type: str = 'desc',
    return_query: bool = False,
    expired_rates_required: bool = False,
    all_rates_for_cogo_assured: bool = False,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    # try:
    data = list_fcl_freight_rates(filters, page_limit, page, sort_by, sort_type, return_query, expired_rates_required, all_rates_for_cogo_assured)
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})


@fcl_freight_router.get("/list_fcl_freight_rate_locals")
def list_fcl_freight_rate_locals_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = 'updated_at',
    sort_type: str = 'desc',
    return_query: bool = False,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    # try:
    data = list_fcl_freight_rate_locals(filters, page_limit, page, sort_by, sort_type, return_query)
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.get("/list_fcl_freight_rate_local_agents")
def list_fcl_freight_rate_local_agent_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = 'updated_at',
    sort_type: str = 'desc',
    pagination_data_required: bool = True,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    # try:
    data = list_fcl_freight_rate_local_agents(filters, page_limit, page, sort_by, sort_type, pagination_data_required)
    data = jsonable_encoder(data)
    return JSONResponse(status_code = 200, content = data)
    # except:
    #     return JSONResponse(status_code = 500, content = {'success':False})

@fcl_freight_router.get("/list_fcl_freight_rate_tasks")
def list_fcl_freight_rate_tasks_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = 'created_at',
    sort_type: str = 'desc',
    stats_required: bool = True,
    pagination_data_required: bool = True,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    # try:
    data = list_fcl_freight_rate_tasks(filters, page_limit, page, sort_by, sort_type, stats_required, pagination_data_required)
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.get("/list_fcl_freight_rate_requests")
def list_fcl_freight_rate_requests_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    performed_by_id: str = None,
    is_stats_required: bool = True,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    # try:
    data = list_fcl_freight_rate_requests(filters, page_limit, page, performed_by_id, is_stats_required)
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.get("/list_fcl_freight_rate_local_requests")
def list_fcl_freight_rate_local_requests_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    performed_by_id: str = None,
    is_stats_required: bool = True,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    # try:
    data = list_fcl_freight_rate_local_requests(filters, page_limit, page, is_stats_required, performed_by_id)
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.get("/list_fcl_freight_rate_seasonal_surcharges")
def list_fcl_freight_rate_seasonal_surcharges_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    pagination_data_required: bool = True,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    # try:
    data = list_fcl_freight_rate_seasonal_surcharges(filters, page_limit, page, pagination_data_required)
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})


@fcl_freight_router.get("/list_fcl_freight_rate_feedbacks")
def list_fcl_freight_rate_feedbacks_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    performed_by_id: str = None,
    is_stats_required: bool = True,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    # try:
    data = list_fcl_freight_rate_feedbacks(filters, page_limit, page, performed_by_id, is_stats_required)
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})


@fcl_freight_router.get("/list_fcl_freight_rate_commodity_clusters")
def list_fcl_freight_rate_commodity_clusters_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    pagination_data_required: bool = True,
    sort_by: str = 'updated_at',
    sort_type: str = 'desc',
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    # try:
    data = list_fcl_freight_commodity_clusters(filters, page_limit, page, pagination_data_required, sort_by, sort_type)
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.get("/list_fcl_freight_rate_commodity_surcharges")
def list_fcl_freight_rate_commodity_surcharges_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    pagination_data_required: bool = True,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    # try:
    data = list_fcl_freight_rate_commodity_surcharges(filters, page_limit, page, pagination_data_required)
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.get("/list_fcl_freight_rate_dislikes")
def list_fcl_freight_rate_dislikes_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    # try:
    data = list_fcl_freight_rate_dislikes(filters, page_limit, page)
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.get("/list_fcl_freight_rate_local_suggestions")
def list_fcl_freight_local_suggestions_data(
    service_provider_id: str,
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = 'updated_at',
    sort_type: str = 'desc',
    pagination_data_required: bool = True,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)
    # try:
    data = list_fcl_freight_rate_local_suggestions(service_provider_id, filters, page_limit, page, sort_by, sort_type, pagination_data_required)
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.get("/list_fcl_freight_rate_free_days")
def list_fcl_freight_rate_free_days_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    pagination_data_required: bool = True,
    return_query: bool = False,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    # try:
    data = list_fcl_freight_rate_free_days(filters, page_limit, page, pagination_data_required, return_query)
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.get("/list_fcl_freight_rate_weight_limits")
def list_fcl_freight_rate_weight_limits_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    pagination_data_required: bool = True,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    # try:
    data = list_fcl_freight_rate_weight_limits(filters, page_limit, page, pagination_data_required)
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.get("/list_fcl_weight_slabs_configuration")
def list_fcl_weight_slabs_configuration_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    pagination_data_required: bool = True,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    # try:
    data = list_fcl_weight_slabs_configuration(filters, page_limit, page, pagination_data_required)
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.post("/update_fcl_freight_rate")
def update_fcl_freight_rate(request: UpdateFclFreightRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    data = update_fcl_freight_rate_data(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})


@fcl_freight_router.put("/update_fcl_freight_rate_local")
def update_fcl_freight_rate_local_data(request: UpdateFclFreightRateLocal, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    data = update_fcl_freight_rate_local(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.put("/update_fcl_freight_rate_local_agent")
def update_fcl_freight_rate_local_agent_data(request: UpdateFclFreightRateLocalAgent, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    data = update_fcl_freight_rate_local_agent(request.__dict__)
    data = jsonable_encoder(data)
    return JSONResponse(status_code=200, content=data)
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.put("/update_fcl_weight_slabs_configuration")
def update_fcl_weight_slabs_configuration_data(request: UpdateFclWeightSlabsConfiguration, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    data = update_fcl_weight_slabs_configuration(request.dict(exclude_none=True))
    data = jsonable_encoder(data)
    return JSONResponse(status_code=200, content=data)
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.put("/update_fcl_freight_rate_platform_prices")
def update_fcl_freight_rate_platform_prices_data(request: UpdateFclFreightRatePlatformPrices, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    data = update_fcl_freight_rate_platform_prices(request.dict(exclude_none=False))
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.delete("/delete_fcl_freight_rate")
def delete_fcl_freight_rates(request: DeleteFclFreightRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    delete_rate = delete_fcl_freight_rate(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content=jsonable_encoder(delete_rate))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.post("/create_fcl_freight_rate_extension_rule_set")
def create_fcl_freight_rate_extension_rule_set(request: PostFclFreightRateExtensionRuleSet, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    data = create_fcl_freight_rate_extension_rule_set_data(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.post("/extend_create_fcl_freight_rate")
def extend_create_fcl_freight_rate(request: ExtendCreateFclFreightRate):
    return extend_create_fcl_freight_rate_data(request)

@fcl_freight_router.post("/update_fcl_freight_rate_extension_rule_set")
def update_fcl_freight_rate_extension_rule_set(request: UpdateFclFreightRateExtensionRuleSet, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    data = update_fcl_freight_rate_extension_rule_set_data(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.get("/list_fcl_freight_rate_extension_rule_set")
def list_fcl_freight_rate_extension_rule_set(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = 'updated_at',
    sort_type: str = 'desc',
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    # try:
    data =  list_fcl_freight_rate_extension_rule_set_data(filters, page_limit, page, sort_by, sort_type)
    data = jsonable_encoder(data)
    return JSONResponse(status_code=200, content=data)
    # except:
    #     return JSONResponse(status_code=500, content={'success':False})


@fcl_freight_router.get("/get_fcl_freight_rate_extension")
def get_fcl_freight_rate_extension(
    service_provider_id: str,
    shipping_line_id: str,
    origin_port_id: str,
    destination_port_id: str,
    commodity: str,
    container_size: str,
    container_type:str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    # try:
    data = get_fcl_freight_rate_extension_data(service_provider_id, shipping_line_id, origin_port_id, destination_port_id, commodity, container_size, container_type)
    data = jsonable_encoder(data)
    return JSONResponse(status_code=200, content=data)
    # except:
    #     return JSONResponse(status_code=500, content={'success':False})


# @fcl_freight_router.post("/update_fcl_freight_rate_task")
# def update_fcl_freight_rate_task(request: UpdateFclFreightRateTask):
#     return update_fcl_freight_rate_task_data(request)


@fcl_freight_router.delete("/delete_fcl_freight_rate_request")
def delete_fcl_freight_rates_request(request: DeleteFclFreightRateRequest, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    delete_rate = delete_fcl_freight_rate_request(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content=jsonable_encoder(delete_rate))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.delete("/delete_fcl_freight_rate_feedback")
def delete_fcl_freight_rates_feedback(request: DeleteFclFreightRateFeedback, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    delete_rate = delete_fcl_freight_rate_feedback(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content=jsonable_encoder(delete_rate))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.delete("/delete_fcl_freight_rate_local_request")
def delete_fcl_freight_rates_local_request(request: DeleteFclFreightRateLocalRequest, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    delete_rate = delete_fcl_freight_rate_local_request(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content=jsonable_encoder(delete_rate))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.delete("/delete_fcl_freight_rate_local")
def delete_fcl_freight_rates_local(request: DeleteFclFreightRateLocal, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    delete_rate = delete_fcl_freight_rate_local(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content=jsonable_encoder(delete_rate))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.delete("/delete_fcl_freight_rate_free_day_request")
def delete_fcl_freight_rates_free_day_request(request: DeleteFclFreightRateFreeDayRequest, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    delete_rate = delete_fcl_freight_rate_free_day_request(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content=jsonable_encoder(delete_rate))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})


@fcl_freight_router.post("/create_fcl_freight_rate_weight_limit")
def create_fcl_freight_rate_weight_limit_data(request: CreateFclFreightRateWeightLimit, resp:dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    data = create_fcl_freight_rate_weight_limit(request.dict(exclude_none=False))
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.get("/get_fcl_freight_rate_weight_limit")
def get_fcl_freight_rate_weight_limit_data(
    origin_location_id: str = None,
    destination_location_id: str = None,
    container_size: str = None,
    container_type: str = None,
    shipping_line_id: str = None,
    service_provider_id: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        'origin_location_id':origin_location_id,
        'destination_location_id':destination_location_id,
        'container_size':container_size,
        'container_type':container_type,
        'shipping_line_id': shipping_line_id,
        'service_provider_id':service_provider_id
    }
    # try:
    data = get_fcl_freight_rate_weight_limit(request)
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.put("/update_fcl_freight_rate_weight_limit")
def update_fcl_freight_rate_weight_limit_data(request: UpdateFclFreightRateWeightLimit, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    data = update_fcl_freight_rate_weight_limit(request.dict(exclude_none=False))
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.post("/create_fcl_freight_rate_free_day")
def create_fcl_freight_rate_free_day_data(request: CreateFclFreightRateFreeDay, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_fcl_freight_rate_free_day(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except Exception as e:
        raise e

@fcl_freight_router.get("/get_fcl_freight_rate_free_day")
def get_fcl_freight_rate_free_day_data(
    location_id: str = None,
    trade_type: str = None,
    free_days_type: str = None,
    container_size: str = None,
    container_type: str = None,
    shipping_line_id: str = None,
    service_provider_id: str = None,
    importer_exporter_id: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

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
    # try:
    data = get_fcl_freight_rate_free_day(request)
    data = jsonable_encoder(data)
    return JSONResponse(status_code=200, content= data)
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})


@fcl_freight_router.get("/get_eligible_fcl_freight_rate_free_day")
def get_eligible_fcl_freight_rate_free_day_data(
    filters: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    # try:
    data = get_eligible_fcl_freight_rate_free_day(filters)
    data = jsonable_encoder(data)
    return JSONResponse(status_code=200, content= data)
    # except:
    #     return JSONResponse(status_code= 500, content= {'success':False})

@fcl_freight_router.post("/update_fcl_freight_rate_free_day")
def update_fcl_freight_rate_free_day_data(request: UpdateFclFreightRateFreeDay, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    data = update_fcl_freight_rate_free_day(request.dict(exclude_none=False))
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.get("/get_fcl_freight_rate_stats")
def get_fcl_freight_rate_stats_data(
    validity_start: str,
    validity_end: str,
    stats_types: Union[List[str],None]= Query(None),
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    validity_start = datetime.strptime(validity_start, '%Y-%m-%d').date().isoformat()
    validity_end = datetime.strptime(validity_end, '%Y-%m-%d').date().isoformat()
    request = {
        'validity_start':validity_start,
        'validity_end':validity_end,
        'stats_types':stats_types
    }
    # try:
    data = get_fcl_freight_rate_stats(request)
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.get("/get_fcl_freight_rate_seasonal_surcharge")
def get_fcl_freight_rate_seasonal_surcharge_data(
    origin_location_id: str = None,
    destination_location_id: str = None,
    container_size: str = None,
    container_type: str = None,
    code: str = None,
    shipping_line_id: str = None,
    service_provider_id: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    request = {
        'origin_location_id':origin_location_id,
        'destination_location_id':destination_location_id,
        'container_size':container_size,
        'container_type':container_type,
        'code':code,
        'shipping_line_id':shipping_line_id,
        'service_provider_id':service_provider_id
    }
    # try:
    data = get_fcl_freight_rate_seasonal_surcharge(request)
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.get("/get_fcl_freight_rate_commodity_surcharge")
def get_fcl_freight_rate_commodity_surcharge_data(
    origin_location_id: str = None,
    destination_location_id: str = None,
    container_size: str = None,
    container_type: str = None,
    commodity: str = None,
    shipping_line_id: str = None,
    service_provider_id: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    request = {
        'origin_location_id':origin_location_id,
        'destination_location_id':destination_location_id,
        'container_size':container_size,
        'container_type':container_type,
        'commodity':commodity,
        'shipping_line_id':shipping_line_id,
        'service_provider_id':service_provider_id
    }
    # try:
    data = get_fcl_freight_rate_commodity_surcharge(request)
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.get("/get_fcl_freight_commodity_cluster")
def get_fcl_freight_commodity_cluster_data(
    id: str,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    # try:
    data = get_fcl_freight_commodity_cluster(id)
    data = jsonable_encoder(data)
    return JSONResponse(status_code = 200, content = data)
    # except:
    #     return JSONResponse(status_code = 500, content = {'success' : False})

@fcl_freight_router.post('/update_fcl_freight_commodity_cluster')
def update_fcl_freight_commodity_cluster_data(request:UpdateFclFreightCommodityCluster, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    data = update_fcl_freight_commodity_cluster(request)
    data = jsonable_encoder(data)
    return JSONResponse(status_code=200, content = data)
    # except:
    #     return JSONResponse(status_code=500, content = {'success':False})

@fcl_freight_router.post('/update_fcl_freight_commodity_surcharge')
def update_fcl_freight_commodity_surcharge_data(request:UpdateFclFreightRateCommoditySurcharge, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    data = update_fcl_freight_rate_commodity_surcharge(request.dict(exclude_none=False))
    return JSONResponse(status_code=200, content = jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content = {'success':False})


@fcl_freight_router.post("/create_fcl_freight_rate_seasonal_surcharge")
def create_fcl_freight_rate_seasonal_surcharge_data(request: CreateFclFreightSeasonalSurcharge, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    data = create_fcl_freight_rate_seasonal_surcharge(request.dict(exclude_none=False))
    return JSONResponse(status_code=200 ,content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})


@fcl_freight_router.post("/create_fcl_freight_rate_bulk_operation")
def create_fcl_freight_rate_bulk_operation_data(request:CreateBulkOperation, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    data=create_fcl_freight_rate_bulk_operation(request.dict(exclude_none=True))
    return JSONResponse(content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})



@fcl_freight_router.post("/create_fcl_freight_rate_free_day_request")
def create_fcl_freight_rate_free_day_requests(request: CreateFclFreightRateFreeDayRequest, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    data = create_fcl_freight_rate_free_day_request(request.dict(exclude_none=False))
    return JSONResponse(status_code=200 ,content=jsonable_encoder(data))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})

@fcl_freight_router.post("/create_fcl_rate_sheet")
def create_rate_sheets(request: CreateRateSheet):
    # if resp["status_code"] != 200:
    #     return JSONResponse(status_code=resp["status_code"], content=resp)
    # if resp["isAuthorized"]:
        # request.performed_by_id = resp["setters"]["performed_by_id"]
        # request.performed_by_type = resp["setters"]["performed_by_type"]
    # try:
    rate_sheet = create_rate_sheet(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content=jsonable_encoder(rate_sheet))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})



@fcl_freight_router.post("/update_fcl_rate_sheet")
def update_rate_sheets(request: UpdateRateSheet):
    # if resp["status_code"] != 200:
    #     return JSONResponse(status_code=resp["status_code"], content=resp)
    # if resp["isAuthorized"]:
    #     request.performed_by_id = resp["setters"]["performed_by_id"]
    #     request.performed_by_type = resp["setters"]["performed_by_type"]

    # try:
    rate_sheet =update_rate_sheet(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content=jsonable_encoder(rate_sheet))
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})


@fcl_freight_router.get("/list_fcl_rate_sheets")
def list_rates_sheets(
    filters: str = None,
    stats_required: bool = True,
    page: int = 1,
    page_limit: int = 10,
    sort_by: str = 'created_at',
    sort_type: str = 'desc',
    pagination_data_required:  bool = True
    # resp: dict = Depends(authorize_token)
):
    # if resp["status_code"] != 200:
    #     return JSONResponse(status_code=resp["status_code"], content=resp)

    # try:
    response = list_rate_sheets(
        filters, stats_required, page, page_limit,sort_by, sort_type, pagination_data_required
    )
    return JSONResponse(status_code=200, content=response)
    # except:
    #     return JSONResponse(status_code=500, content={"success": False})


