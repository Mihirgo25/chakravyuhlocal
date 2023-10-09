from services.fcl_customs_rate.fcl_customs_params import *
from rms_utils.auth import authorize_token
from fastapi import APIRouter, Depends
from libs.json_encoder import json_encoder
from fastapi.responses import JSONResponse
import sentry_sdk, traceback
from fastapi import HTTPException
import json
from params import CreateRateSheet, UpdateRateSheet

from services.fcl_customs_rate.interaction.create_fcl_customs_rate import create_fcl_customs_rate
from services.fcl_customs_rate.interaction.create_fcl_customs_rate_bulk_operation import create_fcl_customs_rate_bulk_operation
from services.fcl_customs_rate.interaction.create_fcl_customs_rate_feedback import create_fcl_customs_rate_feedback
from services.fcl_customs_rate.interaction.create_fcl_customs_rate_request import create_fcl_customs_rate_request
from services.fcl_customs_rate.interaction.create_fcl_customs_rate_not_available import create_fcl_customs_rate_not_available
from services.fcl_customs_rate.interaction.get_fcl_customs_rate_addition_frequency import get_fcl_customs_rate_addition_frequency
from services.fcl_customs_rate.interaction.get_fcl_customs_rate_visibility import get_fcl_customs_rate_visibility
from services.fcl_customs_rate.interaction.get_fcl_customs_rate import get_fcl_customs_rate
from services.fcl_customs_rate.interaction.list_fcl_customs_rates import list_fcl_customs_rates
from services.fcl_customs_rate.interaction.list_fcl_customs_rate_requests import list_fcl_customs_rate_requests
from services.fcl_customs_rate.interaction.list_fcl_customs_rate_feedbacks import list_fcl_customs_rate_feedbacks
from services.fcl_customs_rate.interaction.update_fcl_customs_rate import update_fcl_customs_rate
from services.fcl_customs_rate.interaction.delete_fcl_customs_rate import delete_fcl_customs_rate
from services.fcl_customs_rate.interaction.update_fcl_customs_rate_platform_prices import update_fcl_customs_rate_platform_prices
from services.fcl_customs_rate.interaction.get_fcl_customs_rate_cards import get_fcl_customs_rate_cards
from services.fcl_customs_rate.interaction.delete_fcl_customs_rate_feedback import delete_fcl_customs_rate_feedback
from services.fcl_customs_rate.interaction.delete_fcl_customs_rate_request import delete_fcl_customs_rate_request
from services.rate_sheet.interactions.create_rate_sheet import create_rate_sheet
from services.rate_sheet.interactions.update_rate_sheet import update_rate_sheet
from services.rate_sheet.interactions.list_rate_sheets import list_rate_sheets
from services.rate_sheet.interactions.list_rate_sheet_stats import list_rate_sheet_stats
from services.fcl_customs_rate.interaction.delete_fcl_customs_rate_job import delete_fcl_customs_rate_job
from services.fcl_customs_rate.interaction.list_fcl_customs_rate_jobs import list_fcl_customs_rate_jobs
from services.fcl_customs_rate.interaction.get_fcl_customs_rate_job_stats import get_fcl_customs_rate_job_stats
from services.fcl_customs_rate.interaction.create_fcl_customs_rate_job import create_fcl_customs_rate_job
from services.fcl_customs_rate.interaction.update_fcl_customs_rate_job import update_fcl_customs_rate_job

fcl_customs_router = APIRouter()

@fcl_customs_router.post("/create_fcl_customs_rate")
def create_fcl_customs_rate_api(request: CreateFclCustomsRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]

    try:
        rate = create_fcl_customs_rate(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e), 'traceback': traceback.print_exc() })

@fcl_customs_router.post("/create_fcl_customs_rate_bulk_operation")
def create_fcl_customs_rate_bulk_operation_api(request: CreateFclCustomsRateBulkOperation, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = create_fcl_customs_rate_bulk_operation(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@fcl_customs_router.post("/create_fcl_customs_rate_feedback")
def create_fcl_customs_rate_feedback_api(request: CreateFclCustomsRateFeedback, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = create_fcl_customs_rate_feedback(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@fcl_customs_router.post("/create_fcl_customs_rate_request")
def create_fcl_customs_rate_request_api(request: CreateFclCustomsRateRequest, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = create_fcl_customs_rate_request(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@fcl_customs_router.post("/create_fcl_customs_rate_not_available")
def create_fcl_customs_rate_not_available_api(request: CreateFclCustomsRateNotAvailable, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = create_fcl_customs_rate_not_available(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@fcl_customs_router.get("/get_fcl_customs_rate_addition_frequency")
def get_fcl_customs_rate_addition_frequency_api(
    group_by: str,
    filters: str = None,
    sort_type: str = 'desc',
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = get_fcl_customs_rate_addition_frequency(group_by, filters, sort_type)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    

@fcl_customs_router.get("/get_fcl_customs_rate_visibility")
def get_fcl_customs_rate_visibility_api(
    service_provider_id: str,
    location_id: str = None,
    rate_id: str = None,
    container_size: str = None,
    container_type: str = None,
    commodity: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        'service_provider_id' : service_provider_id,
        'location_id': location_id,
        'rate_id': rate_id,
        'container_size': container_size,
        'container_type': container_type,
        'commodity': commodity
    }
    try:
        data = get_fcl_customs_rate_visibility(request)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@fcl_customs_router.get("/get_fcl_customs_rate")
def get_fcl_customs_rate_api(
    id: str = None,
    location_id: str = None,
    container_size: str = None,
    container_type: str = None,
    commodity: str = None,
    service_provider_id: str = None,
    importer_exporter_id: str = None,
    trade_type: str = None,
    rate_type: str = 'market_place',
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        'id':id,
        'location_id':location_id,
        'container_size' : container_size,
        'container_type' : container_type,
        'commodity' : commodity,
        'service_provider_id': service_provider_id,
        'importer_exporter_id': importer_exporter_id,
        'trade_type': trade_type,
        'rate_type' : rate_type
    }

    try:
        data = get_fcl_customs_rate(request)
        data = json_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    

@fcl_customs_router.get("/list_fcl_customs_rate_feedbacks")
def list_fcl_customs_rate_feedbacks_api(
    filters: str = None,
    spot_search_details_required: bool = False,
    page_limit: int = 10,
    page: int = 1,
    performed_by_id: str = None,
    is_stats_required: bool = True,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_fcl_customs_rate_feedbacks(filters, spot_search_details_required, page_limit, page, performed_by_id, is_stats_required)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@fcl_customs_router.get("/list_fcl_customs_rate_requests")
def list_fcl_customs_rate_requests_api(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    performed_by_id: str = None,
    is_stats_required: bool = True,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_fcl_customs_rate_requests(filters, page_limit, page, performed_by_id, is_stats_required)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@fcl_customs_router.get("/list_fcl_customs_rates")
def list_fcl_customs_rates_api(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = 'updated_at',
    sort_type: str = 'desc',
    pagination_data_required: bool = False,
    return_query: bool = False,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_fcl_customs_rates(filters, page_limit, page, sort_by, sort_type, return_query, pagination_data_required)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    

@fcl_customs_router.get("/get_fcl_customs_rate_cards")
def get_fcl_customs_rate_cards_api(
    port_id: str,
    country_id: str,
    container_size: str,
    container_type: str,
    containers_count: int,
    cargo_handling_type: str = None,
    trade_type: str = None,
    include_confirmed_inventory_rates: bool = True,
    importer_exporter_id: str = None,
    bls_count: int = 1,
    commodity: str = None,
    additional_services: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    if additional_services:
        additional_services = json.loads(additional_services)
    else:
        additional_services = []
    if not importer_exporter_id:
        importer_exporter_id = None
    request = {
        'port_id' : port_id,
        'country_id' : country_id,
        'container_size' : container_size,
        'container_type' : container_type,
        'containers_count' : containers_count,
        'bls_count' : bls_count,
        'commodity' : commodity,
        'importer_exporter_id' : importer_exporter_id,
        'trade_type' : trade_type,
        'cargo_handling_type' : cargo_handling_type,
        'additional_services':additional_services,
        'include_confirmed_inventory_rates':include_confirmed_inventory_rates,
    }

    try:
        data = get_fcl_customs_rate_cards(request)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@fcl_customs_router.post("/update_fcl_customs_rate")
def update_fcl_customs_rate_api(request: UpdateFclCustomsRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = update_fcl_customs_rate(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })


@fcl_customs_router.post("/delete_fcl_customs_rate")
def delete_fcl_customs_rate_api(request: DeleteFclCustomsRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = delete_fcl_customs_rate(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@fcl_customs_router.post("/delete_fcl_customs_rate_feedback")
def delete_fcl_customs_rate_feedback_api(request: DeleteFclCustomsRateFeedback, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = delete_fcl_customs_rate_feedback(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@fcl_customs_router.post("/delete_fcl_customs_rate_request")
def delete_fcl_customs_rate_request_api(request: DeleteFclCustomsRateRequest, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = delete_fcl_customs_rate_request(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
    
@fcl_customs_router.post("/update_fcl_customs_rate_platform_prices")
def update_fcl_customs_rate_platform_prices_api(request: UpdateFclCustomsRatePlatformPrices, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = update_fcl_customs_rate_platform_prices(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@fcl_customs_router.post("/create_fcl_customs_rate_sheet")
def create_rate_sheet_api(request: CreateRateSheet, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate_sheet = create_rate_sheet(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate_sheet))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@fcl_customs_router.post("/update_fcl_customs_rate_sheet")
def update_rate_sheet_api(request: UpdateRateSheet, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]

    try:
        rate_sheet =update_rate_sheet(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate_sheet))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@fcl_customs_router.get("/list_fcl_customs_rate_sheets")
def list_rate_sheets_api(
    filters: str = None,
    stats_required: bool = True,
    page: int = 1,
    page_limit: int = 10,
    sort_by: str = 'created_at',
    sort_type: str = 'desc',
    pagination_data_required:  bool = True,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        response = list_rate_sheets(
            filters, stats_required, page, page_limit,sort_by, sort_type, pagination_data_required
        )
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@fcl_customs_router.get("/list_fcl_customs_rate_sheet_stats")
def list_rates_sheet_stats_api(
    filters: str = None,
    service_provider_id: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        response = list_rate_sheet_stats(
            filters, service_provider_id
        )
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@fcl_customs_router.get("/get_fcl_customs_rate_job_stats")
def get_fcl_customs_rate_job_stats_api(
    filters: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = get_fcl_customs_rate_job_stats(filters)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })



@fcl_customs_router.get("/list_fcl_customs_rate_jobs")
def list_fcl_customs_rate_jobs_api(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = 'updated_at',
    sort_type: str = 'desc',
    generate_csv_url: bool = False,
    includes: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_fcl_customs_rate_jobs(filters, page_limit, page, sort_by, sort_type, generate_csv_url, includes)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@fcl_customs_router.post("/delete_fcl_customs_rate_job")
def delete_fcl_customs_rate_job_api(
    request: DeleteFclCustomsRateJob, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    try:
        rate = delete_fcl_customs_rate_job(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )
    
@fcl_customs_router.get("/get_fcl_customs_rate_job_csv_url")
def get_fcl_customs_rate_job_csv_url_api(
    filters: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_fcl_customs_rate_jobs(filters, generate_csv_url=True)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@fcl_customs_router.post("/create_fcl_customs_rate_job")
def create_fcl_customs_rate_job_api(
    request: CreateFclCustomsRateJob, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    source = request.source
    try:
        rate = create_fcl_customs_rate_job(request.dict(exclude_none=True), source)
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )
        
@fcl_customs_router.post("/update_fcl_customs_rate_job")    
def update_fcl_customs_rate_job_api(
    request: UpdateFclCustomsRateJob, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    try:
        data = update_fcl_customs_rate_job(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })