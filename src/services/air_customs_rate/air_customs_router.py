from services.air_customs_rate.air_customs_params import *
from params import CreateRateSheet, UpdateRateSheet
from rms_utils.auth import authorize_token
from fastapi import APIRouter, Depends
from libs.json_encoder import json_encoder
from fastapi.responses import JSONResponse
import sentry_sdk, traceback
from fastapi import HTTPException
import json
from services.air_customs_rate.interaction.create_air_customs_rate import create_air_customs_rate
from services.air_customs_rate.interaction.create_air_customs_rate_bulk_operation import create_air_customs_rate_bulk_operation
from services.air_customs_rate.interaction.create_air_customs_rate_feedback import create_air_customs_rate_feedback
from services.air_customs_rate.interaction.create_air_customs_rate_request import create_air_customs_rate_request
from services.air_customs_rate.interaction.create_air_customs_rate_not_available import create_air_customs_rate_not_available
from services.air_customs_rate.interaction.get_air_customs_rate_addition_frequency import get_air_customs_rate_addition_frequency
from services.air_customs_rate.interaction.get_air_customs_rate_visibility import get_air_customs_rate_visibility
from services.air_customs_rate.interaction.get_air_customs_rate import get_air_customs_rate
from services.air_customs_rate.interaction.list_air_customs_rates import list_air_customs_rates
from services.air_customs_rate.interaction.list_air_customs_rate_requests import list_air_customs_rate_requests
from services.air_customs_rate.interaction.list_air_customs_rate_feedbacks import list_air_customs_rate_feedbacks
from services.air_customs_rate.interaction.list_air_customs_charge_codes import list_air_customs_charge_codes
from services.air_customs_rate.interaction.update_air_customs_rate import update_air_customs_rate
from services.air_customs_rate.interaction.delete_air_customs_rate import delete_air_customs_rate
from services.air_customs_rate.interaction.delete_air_customs_rate_feedback import delete_air_customs_rate_feedback
from services.air_customs_rate.interaction.delete_air_customs_rate_request import delete_air_customs_rate_request
from services.air_customs_rate.interaction.get_air_customs_rate_cards import get_air_customs_rate_cards

from services.rate_sheet.interactions.create_rate_sheet import create_rate_sheet
from services.rate_sheet.interactions.update_rate_sheet import update_rate_sheet
from services.rate_sheet.interactions.list_rate_sheets import list_rate_sheets
from services.rate_sheet.interactions.list_rate_sheet_stats import list_rate_sheet_stats

air_customs_router = APIRouter()

@air_customs_router.post("/create_air_customs_rate")
def create_air_customs_rate_api(request: CreateAirCustomsRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = create_air_customs_rate(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e), 'traceback': traceback.print_exc() })

@air_customs_router.post("/create_air_customs_rate_bulk_operation")
def create_air_customs_rate_bulk_operation_api(request: CreateAirCustomsRateBulkOperation, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = create_air_customs_rate_bulk_operation(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@air_customs_router.post("/create_air_customs_rate_feedback")
def create_air_customs_rate_feedback_api(request: CreateAirCustomsRateFeedback, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = create_air_customs_rate_feedback(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@air_customs_router.post("/create_air_customs_rate_request")
def create_air_customs_rate_request_api(request: CreateAirCustomsRateRequest, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = create_air_customs_rate_request(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@air_customs_router.post("/create_air_customs_rate_not_available")
def create_air_customs_rate_not_available_api(request: CreateAirCustomsRateNotAvailable, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = create_air_customs_rate_not_available(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@air_customs_router.get("/get_air_customs_rate_addition_frequency")
def get_air_customs_rate_addition_frequency_api(
    group_by: str,
    filters: str = None,
    sort_type: str = 'desc',
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = get_air_customs_rate_addition_frequency(group_by, filters, sort_type)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@air_customs_router.get("/get_air_customs_rate_visibility")
def get_air_customs_rate_visibility_api(
    service_provider_id: str,
    location_id: str = None,
    rate_id: str = None,
    commodity: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        'service_provider_id' : service_provider_id,
        'location_id': location_id,
        'rate_id': rate_id,
        'commodity': commodity
    }
    try:
        data = get_air_customs_rate_visibility(request)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@air_customs_router.get("/get_air_customs_rate")
def get_air_customs_rate_api(
    airport_id: str = None,
    commodity: str = None,
    service_provider_id: str = None,
    importer_exporter_id: str = None,
    trade_type: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        'airport_id':airport_id,
        'commodity' : commodity,
        'service_provider_id': service_provider_id,
        'importer_exporter_id': importer_exporter_id,
        'trade_type': trade_type,
    }

    try:
        data = get_air_customs_rate(request)
        data = json_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })


@air_customs_router.get("/list_air_customs_rate_feedbacks")
def list_air_customs_rate_feedbacks_api(
    filters: str = None,
    spot_search_details_required: bool = False,
    customer_details_required: bool = False,
    page_limit: int = 10,
    page: int = 1,
    performed_by_id: str = None,
    is_stats_required: bool = True,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_air_customs_rate_feedbacks(filters, spot_search_details_required, customer_details_required, page_limit, page, performed_by_id, is_stats_required)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@air_customs_router.get("/list_air_customs_rate_requests")
def list_air_customs_rate_requests_api(
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
        data = list_air_customs_rate_requests(filters, page_limit, page, performed_by_id, is_stats_required)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@air_customs_router.get("/list_air_customs_rates")
def list_air_customs_rates_api(
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
        data = list_air_customs_rates(filters, page_limit, page, sort_by, sort_type,return_query, pagination_data_required)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@air_customs_router.get("/list_air_customs_charge_codes")
def list_air_customs_charge_codes_api(
    service_type: str,
    trade_type: str,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        'service_type': service_type,
        'trade_type': trade_type
    }
    try:
        data = list_air_customs_charge_codes(request)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@air_customs_router.get("/get_air_customs_rate_cards")
def get_air_customs_rate_cards_api(
    airport_id: str,
    trade_type: str,
    weight : float,
    volume: float,
    packages_count : int,
    commodity: str = None,
    importer_exporter_id: str = None,
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
        'airport_id' : airport_id,
        'packages_count' : packages_count,
        'commodity' : commodity,
        'importer_exporter_id' : importer_exporter_id,
        'trade_type' : trade_type,
        'weight' : weight,
        'volume': volume,
        'additional_services':additional_services,
    }

    try:
        data = get_air_customs_rate_cards(request)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@air_customs_router.post("/update_air_customs_rate")
def update_air_customs_rate_api(request: UpdateAirCustomsRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = update_air_customs_rate(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })


@air_customs_router.post("/delete_air_customs_rate")
def delete_air_customs_rate_api(request: DeleteAirCustomsRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = delete_air_customs_rate(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@air_customs_router.post("/delete_air_customs_rate_feedback")
def delete_air_customs_rate_feedback_api(request: DeleteAirCustomsRateFeedback, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = delete_air_customs_rate_feedback(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@air_customs_router.post("/delete_air_customs_rate_request")
def delete_air_customs_rate_request_api(request: DeleteAirCustomsRateRequest, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = delete_air_customs_rate_request(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@air_customs_router.post("/create_air_customs_rate_sheet")
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

@air_customs_router.post("/update_air_customs_rate_sheet")
def update_rate_sheet_api(request: UpdateRateSheet, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]

    try:
        rate_sheet = update_rate_sheet(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate_sheet))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@air_customs_router.get("/list_air_customs_rate_sheets")
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

@air_customs_router.get("/list_air_customs_rate_sheet_stats")
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