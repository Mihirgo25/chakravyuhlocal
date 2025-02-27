from fastapi import APIRouter, Query, Depends
from fastapi.responses import JSONResponse
from typing import List
from libs.json_encoder import json_encoder
from services.fcl_cfs_rate.fcl_cfs_params import *
from rms_utils.auth import authorize_token
import sentry_sdk
from fastapi import HTTPException
from params import CreateRateSheet, UpdateRateSheet

from services.fcl_cfs_rate.interaction.create_fcl_cfs_rate import create_fcl_cfs_rate
from services.fcl_cfs_rate.interaction.get_fcl_cfs_rate import get_fcl_cfs_rate
from services.fcl_cfs_rate.interaction.list_fcl_cfs_rates import list_fcl_cfs_rates
from services.fcl_cfs_rate.interaction.get_fcl_cfs_rate_cards import get_fcl_cfs_rate_cards
from services.fcl_cfs_rate.interaction.list_fcl_cfs_rate_requests import list_fcl_cfs_rate_requests
from services.fcl_cfs_rate.interaction.list_fcl_cfs_rate_feedbacks import list_fcl_cfs_rate_feedbacks
from services.fcl_cfs_rate.interaction.create_fcl_cfs_rate_request import create_fcl_cfs_rate_request
from services.fcl_cfs_rate.interaction.create_fcl_cfs_rate_feedback import create_fcl_cfs_rate_feedback
from services.fcl_cfs_rate.interaction.create_fcl_cfs_rate_not_available import create_fcl_cfs_rate_not_available
from services.fcl_cfs_rate.interaction.delete_fcl_cfs_rate import delete_fcl_cfs_rate
from services.fcl_cfs_rate.interaction.delete_fcl_cfs_rate_request import delete_fcl_cfs_rate_request
from services.fcl_cfs_rate.interaction.delete_fcl_cfs_rate_feedback import delete_fcl_cfs_rate_feedback
from services.fcl_cfs_rate.interaction.update_fcl_cfs_rate import update_fcl_cfs_rate
from services.fcl_cfs_rate.interaction.create_fcl_cfs_rate_bulk_operation import create_fcl_cfs_rate_bulk_operation
from services.fcl_cfs_rate.interaction.update_fcl_cfs_rate_platform_prices import update_fcl_cfs_rate_platform_prices
from services.rate_sheet.interactions.create_rate_sheet import create_rate_sheet
from services.rate_sheet.interactions.update_rate_sheet import update_rate_sheet
from services.rate_sheet.interactions.list_rate_sheets import list_rate_sheets
from services.rate_sheet.interactions.list_rate_sheet_stats import list_rate_sheet_stats
from services.fcl_cfs_rate.interaction.create_fcl_cfs_rate_job import create_fcl_cfs_rate_job
from services.fcl_cfs_rate.interaction.delete_fcl_cfs_rate_job import delete_fcl_cfs_rate_job
from services.fcl_cfs_rate.interaction.get_fcl_cfs_rate_job_stats import get_fcl_cfs_rate_job_stats
from services.fcl_cfs_rate.interaction.list_fcl_cfs_rate_jobs import list_fcl_cfs_rate_jobs
from services.fcl_cfs_rate.fcl_cfs_params import UpdateFclCfsRateJob
from services.fcl_cfs_rate.interaction.update_fcl_cfs_rate_job import update_fcl_cfs_rate_job
fcl_cfs_router = APIRouter()

@fcl_cfs_router.post('/create_fcl_cfs_rate')
def create_fcl_cfs_rate_api(request: CreateFclCfsRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_fcl_cfs_rate(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    

@fcl_cfs_router.post('/create_fcl_cfs_rate_request')
def create_fcl_cfs_rate_request_api(request: CreateFclCfsRateRequest, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_fcl_cfs_rate_request(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@fcl_cfs_router.post('/create_fcl_cfs_rate_not_available')
def create_fcl_cfs_rate_not_available_api(request: CreateFclCfsRateNotAvailable, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_fcl_cfs_rate_not_available(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })


@fcl_cfs_router.post('/create_fcl_cfs_rate_bulk_operation')
def create_fcl_cfs_rate_bulk_operation_api(request: CreateFclCfsRateBulkOperation, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_fcl_cfs_rate_bulk_operation(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })


@fcl_cfs_router.get("/get_fcl_cfs_rate_cards")
def get_fcl_cfs_rate_cards_api(trade_type: str,
                       cargo_handling_type: str,
                       port_id: str,
                       container_size: str,
                       container_type: str,
                       containers_count: int, 
                       bls_count: int = 1,
                       importer_exporter_id: str = None,
                       country_id: str = None,
                       commodity: str = None,
                       cargo_weight_per_container: int = None,
                       additional_services: List[str] | None= Query(None),
                       cargo_value: int = None, 
                       cargo_value_currency: str = None,
                       include_confirmed_inventory_rates: bool = False,
                       resp: dict = Depends(authorize_token)):
    
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)    
    try:
        request = {
            'trade_type':trade_type,
            'cargo_handling_type': cargo_handling_type,
            'port_id':port_id,
            'country_id':country_id,
            'container_size':container_size,
            'container_type':container_type,
            'commodity':commodity,
            'importer_exporter_id':importer_exporter_id,
            'containers_count':containers_count,
            'bls_count':bls_count,
            'cargo_weight_per_container':cargo_weight_per_container,
            'additional_services':additional_services,
            'cargo_value':cargo_value,
            'cargo_value_currency':cargo_value_currency,
            'include_confirmed_inventory_rates':include_confirmed_inventory_rates
        }
        data = get_fcl_cfs_rate_cards(request)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })


@fcl_cfs_router.get("/get_fcl_cfs_rate")
def get_fcl_cfs_rate_api(location_id: str = None,
                    trade_type: str = None,
                    container_size: str = None,
                    container_type: str = None,
                    commodity: str = None,
                    service_provider_id: str = None,
                    importer_exporter_id: str = None,
                    cargo_handling_type: str = None,
                    rate_type: str = "market_place",
                    resp: dict = Depends(authorize_token)
                    ):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        'location_id': location_id,
        'trade_type': trade_type,
        'container_size': container_size,
        'container_type': container_type,
        'commodity': commodity,
        'service_provider_id': service_provider_id,
        'importer_exporter_id': importer_exporter_id,
        'cargo_handling_type': cargo_handling_type,
        'rate_type' : rate_type
    }
    try:
        data = get_fcl_cfs_rate(request)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) }) 


@fcl_cfs_router.get("/list_fcl_cfs_rates")
def list_fcl_cfs_rates_api(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = 'updated_at',
    sort_type: str = 'desc',
    return_query: bool = False,
    pagination_data_required: bool = False,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_fcl_cfs_rates(filters, page_limit, page, sort_by, sort_type,pagination_data_required, return_query)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) }) 

@fcl_cfs_router.get("/list_fcl_cfs_rate_requests") 
def list_fcl_cfs_rate_requests_api(
    filters: str = {},
    page_limit: int = 10,
    page: int = 1,
    is_stats_required: bool = True,
    performed_by_id: str = None,
    resp: dict  = Depends(authorize_token)
    ):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_fcl_cfs_rate_requests(filters, page_limit, page, is_stats_required, performed_by_id)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@fcl_cfs_router.post("/delete_fcl_cfs_rate")
def delete_fcl_cfs_rate_api(request: DeleteFclCfsRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        delete_rate = delete_fcl_cfs_rate(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=json_encoder(delete_rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@fcl_cfs_router.post("/delete_fcl_cfs_rate_request")
def delete_fcl_cfs_rates_request_api(request: DeleteFclCfsRateRequest, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        delete_rate = delete_fcl_cfs_rate_request(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(delete_rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@fcl_cfs_router.post("/update_fcl_cfs_platform_prices")
def update_fcl_cfs_platform_prices_api(request:UpdateFclCfsRatePlatformPrice, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = update_fcl_cfs_rate_platform_prices(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    

@fcl_cfs_router.post('/update_fcl_cfs_rate')
def update_fcl_cfs_rate_api(request: UpdateFclCfsRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = update_fcl_cfs_rate(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@fcl_cfs_router.post("/create_fcl_cfs_rate_sheet")
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

@fcl_cfs_router.post("/update_fcl_cfs_rate_sheet")
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

@fcl_cfs_router.get("/list_fcl_cfs_rate_sheets")
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

@fcl_cfs_router.get("/list_fcl_cfs_rate_sheet_stats")
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

@fcl_cfs_router.post("/create_fcl_cfs_rate_feedback")
def create_fcl_cfs_rate_feedback_api(request: CreateFclCfsRateFeedback, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = create_fcl_cfs_rate_feedback(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@fcl_cfs_router.post("/delete_fcl_cfs_rate_feedback")
def delete_fcl_cfs_rate_feedback_api(request: DeleteFclCfsRateFeedback, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = delete_fcl_cfs_rate_feedback(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@fcl_cfs_router.get("/list_fcl_cfs_rate_feedbacks")
def list_fcl_cfs_rate_feedbacks_api(
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
        data = list_fcl_cfs_rate_feedbacks(filters, spot_search_details_required, page_limit, page, performed_by_id, is_stats_required)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@fcl_cfs_router.get("/get_fcl_cfs_rate_job_stats")
def get_fcl_cfs_rate_job_stats_api(
    filters: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = get_fcl_cfs_rate_job_stats(filters)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })



@fcl_cfs_router.get("/list_fcl_cfs_rate_jobs")
def list_fcl_cfs_rate_jobs_api(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = 'updated_at',
    sort_type: str = 'desc',
    generate_csv_url: bool = False,
    pagination_data_required: bool = False,
    includes: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_fcl_cfs_rate_jobs(filters, page_limit, page, sort_by, sort_type, generate_csv_url, pagination_data_required, includes)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@fcl_cfs_router.post("/delete_fcl_cfs_rate_job")
def delete_fcl_cfs_rate_job_api(
    request: DeleteFclCfsRateJob, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    try:
        rate = delete_fcl_cfs_rate_job(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_cfs_router.get("/get_fcl_cfs_rate_job_csv_url")
def get_fcl_cfs_rate_job_csv_url_api(
    filters: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_fcl_cfs_rate_jobs(filters, generate_csv_url=True)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    

@fcl_cfs_router.post("/create_fcl_cfs_rate_job")
def create_fcl_cfs_rate_job_api(
    request: CreateFclCfsRateJob, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    source = request.source
    try:
        rate = create_fcl_cfs_rate_job(request.dict(exclude_none=True), source)
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )

@fcl_cfs_router.post("/update_fcl_cfs_rate_job")    
def update_fcl_cfs_rate_job_api(
    request: UpdateFclCfsRateJob, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    try:
        data = update_fcl_cfs_rate_job(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })